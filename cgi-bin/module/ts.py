#!/Users/jooyoungkim/.pyenv/versions/2.7.18/bin/python
#coding:utf-8

import re, sys
from mp4 import MP4
from io import BytesIO

# MP4를 MPEG-TS(Transport Stream)로 변환하는 클래스
class TS(MP4):
	def __init__(self, file_name):
		super(TS,self).__init__(file_name)
		self.fileName = file_name
		self.cc = {'video': 0, 'audio': 0, 'pat': 0, 'pmt': 0}

	def _readFS(self, FH, offset, size):
		FH.seek(offset)
		return FH.read(size)

	def _bit_to_bytearray(self, data):
		out = []
		while data:
			(v, data) = (data[0:8], data[8:])
			out.append(int('0b' + v, base=2))
		return bytearray(out)

	def _hex_to_bytearray(self, hex_str):
		if not hex_str: return bytearray()
		return bytearray([int(x, 16) for x in hex_str.strip().split(' ')])

	def _NAL_Convert(self, data):
		bio = BytesIO(data) ; out = bytearray()
		while True:
			l_raw = bio.read(4)
			if not l_raw or len(l_raw) < 4: break
			size = int(l_raw.encode('hex'), 16)
			out += b'\x00\x00\x00\x01' + bio.read(size)
		bio.close()
		return out

	def _ADTS(self, data, freq_idx=4, ch_cfg=2):
		total_len = len(data) + 7
		len_bin = '{:013b}'.format(total_len)
		header = '111111111111' + '0' + '00' + '1' + '01' + '{:04b}'.format(freq_idx) + '0' + '{:03b}'.format(ch_cfg) + '0000' + len_bin + '11111111111' + '00'
		return self._bit_to_bytearray(header) + data

	def _PAT(self, pmt_pid=0x1000):
		pat = '{:08b}'.format(0x00) + '{:08b}'.format(0x00) + '1011'
		body = '{:016b}'.format(0x0001) + '11000001' + '{:016b}'.format(0x00) + '{:016b}'.format(0x0001) + '111' + '{:013b}'.format(pmt_pid)
		body_ba = self._bit_to_bytearray(body) + b'\x2A\xB1\x04\xB2'
		pat += '{:012b}'.format(len(body_ba))
		return self._bit_to_bytearray(pat) + body_ba

	def _PMT(self, pcr_pid=0x100, video_pid=0x100, audio_pid=0x101):
		pmt = '{:08b}'.format(0x00) + '{:08b}'.format(0x02) + '1011'
		body = '{:016b}'.format(0x0001) + '11000001' + '{:016b}'.format(0x00) + '111' + '{:013b}'.format(pcr_pid) + '1111' + '{:012b}'.format(0)
		body += '{:08b}'.format(0x1B) + '111' + '{:013b}'.format(video_pid) + '1111' + '{:012b}'.format(0)
		body += '{:08b}'.format(0x0F) + '111' + '{:013b}'.format(audio_pid) + '1111' + '{:012b}'.format(0)
		body_ba = self._bit_to_bytearray(body) + b'\x8D\x82\x9A\x07'
		pmt += '{:012b}'.format(len(body_ba))
		return self._bit_to_bytearray(pmt) + body_ba

	def _PES(self, type_str, pts, payload_len=0):
		stream_id = 0xE0 if type_str == 'video' else 0xC0
		def format_ts(ts, p):
			b = '{:033b}'.format(int(ts))
			return self._bit_to_bytearray(p + b[0:3] + '1' + b[3:18] + '1' + b[18:33] + '1')
		ts_data = format_ts(pts, '0010')
		# PES Header: [Data Alignment (1bit=1), etc]
		header = self._bit_to_bytearray('10' + '000100' + '10' + '000000' + '{:08b}'.format(len(ts_data))) + ts_data
		# Video(0xE0)는 길이를 0(제한없음)으로, Audio는 실제 데이터 길이를 명시함
		total_pes_len = (len(header) + payload_len) if type_str == 'audio' else 0
		if total_pes_len > 65535: total_pes_len = 0 # 16비트 오버플로우 방지
		return bytearray([0x00, 0x00, 0x01, stream_id, (total_pes_len >> 8) & 0xFF, total_pes_len & 0xFF]) + header

	def _TS_Packet(self, pid, type_name, payload, is_start=False, pcr=None, is_keyframe=False):
		out = bytearray() ; payload = bytearray(payload)
		while payload or (is_start and not payload):
			cc = self.cc[type_name]
			header_bin = '0' + ('1' if is_start else '0') + '0' + '{:013b}'.format(pid) + '00'
			af = bytearray()
			# Keyframe일 경우 random_access_indicator 플래그를 켬 (01010000 -> 01110000 if keyframe)
			af_flags = '01110000' if (is_start and is_keyframe and pcr is not None) else '01010000'
			if is_start and pcr is not None:
				af_body = self._bit_to_bytearray(af_flags + '{:033b}'.format(int(pcr)) + '000000' + '{:09b}'.format(0))
				af = bytearray([len(af_body)]) + af_body
			needed = 184 - len(af)
			if len(payload) < needed:
				stuffing = needed - len(payload)
				if not af: af = bytearray([0x00]) ; stuffing -= 1
				# Adaptation field length 필드 업데이트 및 패딩
				af = bytearray([af[0] + stuffing]) + af[1:] + bytearray([0xFF] * stuffing)
				needed = 184 - len(af)
			header_bin += ('11' if af else '01') + '{:04b}'.format(cc)
			out += b'\x47' + self._bit_to_bytearray(header_bin) + af + payload[:needed]
			payload = payload[needed:] ; self.cc[type_name] = (cc + 1) % 16
			is_start = pcr = is_keyframe = False # 한 번 처리 후 초기화
			if not payload: break
		return out

	def segment(self, seq, duration):
		s = int(seq) if seq is not None else 0
		d = int(duration) if duration is not None else 10
		self.sample = self._sample(s * d, d)
		return self

	def ts(self):
		FH = open(self.fileName, 'rb') ; bio = BytesIO()
		bio.write(self._TS_Packet(0, 'pat', self._PAT(), True))
		bio.write(self._TS_Packet(0x1000, 'pmt', self._PMT(), True))
		
		v_samples = self.sample.get('video', {}).get('sample', [])
		a_samples = self.sample.get('audio', {}).get('sample', [])
		v_info = self.sample.get('video', {}).get('info', {})
		a_info = self.sample.get('audio', {}).get('info', {})

		all_samples = sorted([{'t':'v','d':s} for s in v_samples] + [{'t':'a','d':s} for s in a_samples], key=lambda x:x['d']['time'])

		sps = self._hex_to_bytearray(v_info.get('sps',''))
		pps = self._hex_to_bytearray(v_info.get('pps',''))
		f_idx = a_info.get('freq_index', 4) ; c_cfg = a_info.get('channel_config', 2)

		for item in all_samples:
			s = item['d'] ; raw = self._readFS(FH, s['chunk_offset'], s['sample_size'])
			if item['t'] == 'v':
				ts_val = float(v_info.get('timescale', 90000))
				pts = int(round(s['time'] * 90000.0 / ts_val))
				prefix = b'\x00\x00\x00\x01\x09\xF0'
				is_kf = s.get('keyframe')
				if is_kf: prefix += b'\x00\x00\x00\x01' + sps + b'\x00\x00\x00\x01' + pps
				v_data = prefix + self._NAL_Convert(raw)
				bio.write(self._TS_Packet(0x100, 'video', self._PES('video', pts) + v_data, True, pcr=pts, is_keyframe=is_kf))
			else:
				ts_val = float(a_info.get('timescale', 44100))
				pts = int(round(s['time'] * 90000.0 / ts_val))
				a_data = self._ADTS(raw, f_idx, c_cfg)
				bio.write(self._TS_Packet(0x101, 'audio', self._PES('audio', pts, len(a_data)) + a_data, True))
		FH.close() ; bio.seek(0) ; return bio

	def out(self, seq, sec):
		self.segment(seq, sec)
		data = self.ts().getvalue()
		sys.stdout.write("Content-Type: video/MP2T\n")
		sys.stdout.write("Content-Length: %d\n\n" % len(data))
		sys.stdout.write(data)
		sys.stdout.flush()

if __name__ == '__main__':
	with open('debug.ts', 'wb') as f: f.write(TS('../../BigBuckBunny.mp4').segment(0, 10).ts().read())
	print "debug.ts done."
