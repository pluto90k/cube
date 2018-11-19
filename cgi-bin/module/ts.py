#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4

class TS(MP4):
	def __init__(self, file_name):
		super(TS,self).__init__(file_name)
		self.fileName = file_name

	def _getKey(self, item):
		return item['pts']

	def _findChunkIndex(self, stsc, num):
		count = 0
		for obj in stsc:
			count += obj['sample_per_chunk']
			if num < count:
				return obj['first_chunk_index']

		return 0
	def _sample(self, trak, offset, duration):
		sample = []
		type = trak['mdia']['hdlr']['handler-type']

		if type != 'vide' and type != 'soun':
			return

		mdhd = trak['mdia']['mdhd']
		stbl = trak['mdia']['minf']['stbl']
		stco = stbl['stco']['entry']	#Chunk Offset
		stsz = stbl['stsz']['entry']	#Sample Size
		stsc = stbl['stsc']['entry']	#Sample Count Per Chunk
		stts = stbl['stts']['entry']	#Sample Count PlayTime
		#stss = stbl['stss']['entry']
		#print stco

		timescale = mdhd['timescale']
		time = t_temp = 0
		num = 1

		min = offset * timescale
		max = (offset + duration) * timescale
		pos = -1
		chunk_offet = 0
		for data in stts:
			for n in range(data['count']):
				t_temp += data['delta']
				if t_temp > max: break
				if t_temp > min:

					_pos = self._findChunkIndex(stsc, num) - 1

					if _pos != pos:
						pos = _pos
						chunk_offet = stco[pos]['chunk_offset']

					size = stsz[num - 1]['entry_size']

					pack = {
						"id": num,
						"type": str(type),
						"pts": time / float(timescale),
						"chunk_offset": chunk_offet,
						"sample_size": size
					}

					chunk_offet = chunk_offet + size

					if type == 'vide':
						pack['dts'] = t_temp / float(timescale)

					sample.append(pack)
					time += data['delta']

				num += 1

		return sample

	def segment(self, seq, duration):
		atom = self.dic()['atom']
		traks = atom['moov']['trak']

		timeoffset = seq * duration

		#sampling
		sample = []

		for trak in traks:
			out = self._sample(trak, timeoffset, duration)
			if out: sample.extend(out)

		self.sample = sorted(sample, key=self._getKey)
		return self

	def ts(self):
		FH = open(self.fileName, 'rb')
		for sample in self.sample:

			offset = sample['chunk_offset']
			size = sample['sample_size']

			FH.seek(offset)
			data = FH.read(size)
			print "\n"
			print sample['pts']
			print sample['type']
			print self._hex(data)

		return
		#print sample

	def buffer(self):
		print 'buffer'

if __name__ == '__main__':
	TS('../../BigBuckBunny.mp4').segment(0, 10).ts()
