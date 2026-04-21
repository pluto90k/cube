#!/Users/jooyoungkim/.pyenv/versions/2.7.18/bin/python
#coding:utf-8

import re, sys
from mp4 import MP4
from ts  import TS

# HLS(HTTP Live Streaming) 처리를 위한 클래스
class HLS(MP4):
	def __init__(self, file_name):
		super(HLS,self).__init__(file_name)
		self.fileName = file_name
		self.atom = self.dic()['atom']
		p = re.compile("(.+)\.(mp4)(.+)?")
		g = p.search(file_name)
		self.name = g.group(1)

	# .m3u8 플레이리스트 파일을 생성하여 출력하는 함수
	def m3u8(self, sec=10):
		# 전체 재생 시간 계산
		timescale = self.atom.get('moov', {}).get('mvhd', {}).get('timescale', 90000)
		duration = self.atom.get('moov', {}).get('mvhd', {}).get('duration', 0) // timescale
		total = duration / sec, duration % sec

		if total[1] > 0: total = total[0] + 1
		else: total = total[0]

		# HLS 전용 Content-type 출력
		sys.stdout.write("Content-type: application/vnd.apple.mpegurl\r\n\r\n")
		sys.stdout.write("#EXTM3U\n")
		sys.stdout.write("#EXT-X-TARGETDURATION:%d\n" % (sec))

		t = 0
		# 각 세그먼트 정보 출력
		for i in range(0, total):
			# 각 세그먼트의 샘플 정보 가져오기
			res = self._sample(i, sec)
			
			# 오디오 정보를 우선적으로 사용하여 시간 계산
			track_info = res.get('audio', {})
			samples = track_info.get('sample', [])
			
			if not samples:
				# 오디오가 없으면 비디오 정보 활용
				track_info = res.get('video', {})
				samples = track_info.get('sample', [])
			
			if not samples: continue
			
			first_sample = samples[0]
			last_sample = samples[-1]
			
			# timescale 정보를 트랙의 info 영역에서 가져오도록 수정
			ts_val = track_info.get('info', {}).get('timescale', 90000)
			
			# 실제 인포메이션 시간(초) 계산: (마지막 시간 - 첫 시간) + (1프레임 평균 길이)
			f_time = float(first_sample['time'])
			l_time = float(last_sample['time'])
			frame_dur = (l_time - f_time) / (len(samples) - 1) if len(samples) > 1 else 0
			inf = (l_time - f_time + frame_dur) / float(ts_val)
			
			sys.stdout.write("#EXTINF:%.2f,\n" % (inf))
			t += inf
			# 실제 영상 조각(.ts)을 요청할 URL 출력 (확장자 인식 호환성을 위해 끝에 dummy 파라미터 추가)
			sys.stdout.write("cube.py?file=%s.ts&seq=%d&sec=%d&dummy=.ts\n" % ( self.name, i, sec ))
		
		sys.stdout.write("#EXT-X-ENDLIST\n")

if __name__ == '__main__':
	HLS('../../BigBuckBunny.mp4').m3u8()
