#!/Users/jooyoungkim/.pyenv/versions/2.7.18/bin/python
#coding:utf-8

import sys
import time
from io import BytesIO


# MP4 파일의 바이너리 구조를 파싱하는 클래스
class MP4(object):
	def __init__(self, file_name):
		self.fileName = file_name

	def _hex(self, byte):
		return ' '.join(['%02X' % ord(b) for b in byte])

	def _bin(self, data, size):
		return bin(self._int(data))[2:].zfill(size)

	def _int(self, data):
		if not data: return 0
		return int(data.encode('hex'), 16)

	def _str(self, data):
		return str(data)

	def _time(self, data):
		return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self._int(data)))

	def _read(self, bio, dic):
		while True:
			raw_size = bio.read(4)
			if not raw_size or len(raw_size) < 4: break
			size = self._int(raw_size)
			if size < 8: break 
			tp = self._str(bio.read(4))
			data = bio.read(size - 8)
			self._parser(tp, dic, data)

	def _parser(self, name, dic, data):
		out = {}
		if name == 'moov': out = self._moov(data)
		elif name == 'mvhd': out = self._mvhd(data)
		elif name == 'trak': out = self._trak(data)
		elif name == 'mdia': out = self._media(data)
		elif name == 'mdhd': out = self._mdhd(data)
		elif name == 'minf': out = self._minf(data)
		elif name == 'hdlr': out = self._hdlr(data)
		elif name == 'stbl': out = self._stbl(data)
		elif name == 'stts': out = self._stts(data)
		elif name == 'stss': out = self._stss(data)
		elif name == 'stsd': out = self._stsd(data)
		elif name == 'stco': out = self._stco(data)
		elif name == 'stsz': out = self._stsz(data)
		elif name == 'stsc': out = self._stsc(data)
		
		if dic.has_key(name):
			if isinstance(dic[name], list): dic[name].append(out)
			else: dic[name] = [dic[name], out]
		else: dic[name] = out
		return dic

	def _sample_info(self, data):
		bio = BytesIO(data)
		dic = {}
		# avcC 보직 강화
		raw = data
		idx = raw.find('avcC')
		if idx != -1:
			dic['type'] = 'avcC'
			# avcC 헤더 4바이트 건너뛰기
			info = raw[idx+4:]
			if len(info) > 6:
				# SPS
				c = ord(info[5]) & 31
				dic['sps'] = []
				pos = 6
				for _ in range(c):
					l = (ord(info[pos]) << 8) | ord(info[pos+1])
					pos += 2
					dic['sps'].append(self._hex(info[pos:pos+l]))
					pos += l
				# PPS
				if pos < len(info):
					c = ord(info[pos])
					pos += 1
					dic['pps'] = []
					for _ in range(c):
						l = (ord(info[pos]) << 8) | ord(info[pos+1])
						pos += 2
						dic['pps'].append(self._hex(info[pos:pos+l]))
						pos += l
		# esds 보직 강화
		idx = raw.find('esds')
		if idx != -1:
			dic['type'] = 'esds'
			raw_es = raw[idx+4:]
			idx_05 = raw_es.find('\x05')
			if idx_05 != -1 and len(raw_es) > idx_05 + 2:
				l = ord(raw_es[idx_05+1])
				info = raw_es[idx_05+2 : idx_05+2+l]
				if len(info) >= 2:
					v = (ord(info[0]) << 8) | ord(info[1])
					dic['freq_index'] = (v >> 7) & 0x0F
					dic['channel_config'] = (v >> 3) & 0x0F
		bio.close()
		return dic

	def _sample_parse(self, data):
		bio = BytesIO(data)
		tp = self._str(bio.read(4))
		dic = {'type': tp}
		# stsd entry header skip
		bio.read(6 + 2) # reserved + data_reference_index
		# 엔트리 내부 데이터 전체를 _sample_info에 전달하여 박스 기반으로 찾기
		dic['conf'] = self._sample_info(bio.read())
		bio.close()
		return dic

	def _sample(self, timeoffset, duration):
		atom = self.dic()['atom']
		sample = {}
		traks = atom.get('moov', {}).get('trak', [])
		if not isinstance(traks, list): traks = [traks]
		for trak in traks:
			h = trak.get('mdia', {}).get('hdlr', {}).get('handler-type')
			stbl = trak.get('mdia', {}).get('minf', {}).get('stbl', {})
			stsd = stbl.get('stsd', {}).get('entry', [{}])[0]
			out = self._sampling(trak, timeoffset, duration)
			res = {'sample': out, 'info': {'timescale': trak.get('mdia', {}).get('mdhd', {}).get('timescale', 90000), 'type': stsd.get('type')}}
			if h == 'vide':
				res['info']['pps'] = stsd.get('conf', {}).get('pps', [None])[0]
				res['info']['sps'] = stsd.get('conf', {}).get('sps', [None])[0]
				sample['video'] = res
			elif h == 'soun':
				res['info']['freq_index'] = stsd.get('conf', {}).get('freq_index', 4)
				res['info']['channel_config'] = stsd.get('conf', {}).get('channel_config', 2)
				sample['audio'] = res
		return sample

	def _make_sample_info(self, stsc, stco, stsz):
		info = []
		if not stsc or not stco or not stsz: return []
		
		# 1단계: 청크(Chunk)당 포함된 샘플 수 세팅
		chunk_samples = {}
		total_chunks = len(stco)
		stsc_idx = 0
		for i in range(1, total_chunks + 1):
			if stsc_idx + 1 < len(stsc) and i >= stsc[stsc_idx + 1]['first_chunk_index']:
				stsc_idx += 1
			chunk_samples[i] = stsc[stsc_idx]['sample_per_chunk']
			
		# 2단계: 실제 파일 오프셋 정밀 추출
		sample_idx = 0
		for chunk_idx in range(1, total_chunks + 1):
			offset = stco[chunk_idx - 1]['chunk_offset']
			samples_in_this_chunk = chunk_samples[chunk_idx]
			
			for _ in range(samples_in_this_chunk):
				if sample_idx >= len(stsz): break
				size = stsz[sample_idx]['entry_size']
				info.append({"offset": offset, "size": size})
				offset += size
				sample_idx += 1
			if sample_idx >= len(stsz): break
			
		return info

	def _sampling(self, trak, offset, duration):
		sample = []
		h = trak.get('mdia', {}).get('hdlr', {}).get('handler-type')
		if h not in ['vide', 'soun']: return []
		stbl = trak.get('mdia', {}).get('minf', {}).get('stbl', {})
		s_info = self._make_sample_info(stbl.get('stsc', {}).get('entry', []), stbl.get('stco', {}).get('entry', []), stbl.get('stsz', {}).get('entry', []))
		stss = stbl.get('stss', {}).get('entry', [])
		kf = [obj['sample-number'] for obj in stss]
		ts = trak.get('mdia', {}).get('mdhd', {}).get('timescale', 90000)
		a_t = 0 ; t = 0 ; min_t = offset * ts ; max_t = (offset + duration) * ts
		global_sample_idx = 0
		
		for data in stbl.get('stts', {}).get('entry', []):
			count = data.get('count', 0)
			delta = data.get('delta', 0)
			
			# 최적화: 현재 윈도우 이전의 샘플 세트는 통째로 스킵
			if a_t + (count * delta) <= min_t:
				a_t += count * delta
				t += count * delta
				global_sample_idx += count
				continue

			for _ in range(count):
				a_t += delta
				if a_t > max_t: return sample # 성능을 위해 바로 종료
				if a_t > min_t:
					if global_sample_idx < len(s_info):
						p = {
							"id": len(sample),
							"time": t, # 누적된 실제 프레임 시간(PTS)
							"chunk_offset": s_info[global_sample_idx]['offset'],
							"sample_size": s_info[global_sample_idx]['size']
						}
						if kf: p['keyframe'] = (global_sample_idx + 1) in kf
						sample.append(p)
				t += delta
				global_sample_idx += 1
		return sample

	def _atom(self):
		FH = open(self.fileName, 'rb')
		dic = {}
		while True:
			sz_raw = FH.read(4)
			if not sz_raw or len(sz_raw) < 4: break
			sz = self._int(sz_raw)
			if sz < 8: break
			tp = self._str(FH.read(4))
			self._parser(tp, dic, FH.read(sz - 8))
		FH.close()
		return dic

	def _moov(self, moov):
		dic = {} ; self._read(BytesIO(moov), dic) ; return dic
	def _mvhd(self, mvhd):
		bio = BytesIO(mvhd) ; v = ord(bio.read(1)) ; bio.read(3) ; s = 8 if v else 4
		bio.read(s*2) ; ts = self._int(bio.read(s)) ; du = self._int(bio.read(s)) ; bio.close()
		return {'timescale': ts, 'duration': du}
	def _trak(self, trak):
		dic = {} ; self._read(BytesIO(trak), dic) ; return dic
	def _media(self, media):
		dic = {} ; self._read(BytesIO(media), dic) ; return dic
	def _mdhd(self, mdhd):
		bio = BytesIO(mdhd) ; v = ord(bio.read(1)) ; bio.read(3) ; s = 8 if v else 4
		bio.read(s*2) ; ts = self._int(bio.read(s)) ; bio.close()
		return {'timescale': ts}
	def _minf(self, minf):
		dic = {} ; self._read(BytesIO(minf), dic) ; return dic
	def _hdlr(self, hdlr):
		bio = BytesIO(hdlr) ; bio.read(8) ; t = self._str(bio.read(4)) ; bio.close() ; return {'handler-type': t}
	def _stbl(self, stbl):
		dic = {} ; self._read(BytesIO(stbl), dic) ; return dic
	def _stsd(self, stsd):
		bio = BytesIO(stsd) ; bio.read(8) ; return {'entry':[self._sample_parse(bio.read())]}
	def _stss(self, stss):
		bio = BytesIO(stss) ; bio.read(4) ; c = self._int(bio.read(4))
		return {'entry':[{'sample-number': self._int(bio.read(4))} for _ in range(c)]}
	def _stts(self, stts):
		bio = BytesIO(stts) ; bio.read(4) ; c = self._int(bio.read(4))
		return {'entry':[{'count': self._int(bio.read(4)), 'delta': self._int(bio.read(4))} for _ in range(c)]}
	def _stsc(self, stsc):
		bio = BytesIO(stsc) ; bio.read(4) ; c = self._int(bio.read(4))
		# stsc 엔트리는 3개의 4바이트 필드(first_chunk, samples_per_chunk, sample_description_index)로 구성됨
		return {'entry':[{'first_chunk_index': self._int(bio.read(4)), 'sample_per_chunk': self._int(bio.read(4)), 'sample_description_index': self._int(bio.read(4))} for _ in range(c)]}
	def _stco(self, stco):
		bio = BytesIO(stco) ; bio.read(4) ; c = self._int(bio.read(4))
		return {'entry':[{'chunk_offset': self._int(bio.read(4))} for _ in range(c)]}
	def _stsz(self, stsz):
		bio = BytesIO(stsz) ; bio.read(4)
		sample_size = self._int(bio.read(4))
		c = self._int(bio.read(4))
		# sample_size가 0이 아니면 모든 샘플이 동일한 크기를 가짐
		if sample_size > 0:
			return {'entry':[{'entry_size': sample_size} for _ in range(c)]}
		return {'entry':[{'entry_size': self._int(bio.read(4))} for _ in range(c)]}

	def dic(self): return {"filename": self.fileName, "atom": self._atom()}

if __name__ == '__main__':
	import json
	print json.dumps(MP4('BigBuckBunny.mp4').dic(), indent=2)
