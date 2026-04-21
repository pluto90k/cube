#!/Users/jooyoungkim/.pyenv/versions/2.7.18/bin/python
#coding:utf-8

import cgi, re, json, sys, os
# 표준 출력을 바이너리 모드(unbuffered)로 재설정하여 데이터 오염 방지
sys.stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
from module.hls import HLS
from module.mp4 import MP4
from module.ts import TS

# JSON 응답을 출력하는 유틸리티 함수
def _json(data):
	json_data = json.dumps(data)
	sys.stdout.write("Content-type: application/json\r\n")
	sys.stdout.write("Content-Length: %d\r\n\r\n" % len(json_data))
	sys.stdout.write(json_data)

# MP4 파일을 직접 스트리밍 출력하는 함수
def _out(filename, chunk_size=1024):
	out_file = sys.stdout
	head =  "Accept-Ranges: bytes\r\n"
	head += "Content-Type: video/mp4\r\n"
	head += "Content-Length: %ld\r\n\r\n" % os.stat(filename).st_size

	fo = open(filename, "rb")
	sys.stdout.write(head)

	# 파일을 읽어 표준 출력(stdout)으로 바이너리 데이터 전송
	while True:
		out = fo.read(chunk_size)
		if out:
			out_file.write(out)
		else:
			break;

	fo.close()

# CGI 파라미터 받기
form = cgi.FieldStorage()
fileName = form.getvalue('file')

# 정규표현식을 통해 요청된 파일명과 확장자 추출
p = re.compile("(.+)\.(mp4|json|m3u8|ts)(.+)?")
g = p.search(fileName)

data = {'error':'none', 'data':None}

if g:
	fileName = g.group(1)	    # 파일명 추출
	ext = g.group(2)  		# 확장자 추출

	# 기반이 되는 mp4 파일 경로 설정
	fileName = "%s.%s" % (fileName, 'mp4')

	if not os.path.exists(fileName):     # 실제 파일 존재 여부 확인
		data["error"] = "Unknown File"
		_json(data)
	elif ext == 'json':					# 미디어 상세 정보 요청 시
		data["error"] = "none"
		data["data"] = MP4(fileName).dic() # MP4 모듈을 통해 메타데이터 추출
		_json(data)
	elif ext == 'mp4':  				# 일반 MP4 스트리밍 요청 시
		_out(fileName)
	elif ext == 'm3u8':  				# HLS 플레이리스트 요청 시
		HLS(fileName).m3u8()            # HLS 모듈을 통해 .m3u8 생성 출력
	elif ext == 'ts':                   # HLS 영상 조각 요청 시
		seq = form.getvalue('seq')
		sec = form.getvalue('sec')
		# TS 모듈의 출력 함수 호출 (seq: 시퀀스 번호, sec: 조각당 시간)
		TS(fileName).out(seq, sec)

else:
	data["error"] = "Unknown File"
	_json(data)
