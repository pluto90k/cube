#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4

class TS(MP4):
	def __init__(self, file_name):
		super(TS,self).__init__(file_name)
		self.fileName = file_name

	def _parse(self, stts, offset, duration, timescale):

		num = time = t_temp = 0
		offset_num = 1

		min = offset * timescale
		max = (offset + duration) * timescale

		for data in stts:
			for n in range(data['count']):
				t_temp += data['delta']
				if t_temp > max: return (offset_num, num, time)
				if t_temp > min:
					time += data['delta']
				else:
					offset_num += 1

				num += 1

	def segment(self, seq, duration):
		atom = self.dic()['atom']
		traks = atom['moov']['trak']

		timeoffset = seq * duration

		for trak in traks:
			if trak['mdia']['hdlr']['handler-type'] == 'vide':
				mdhd = trak['mdia']['mdhd']
				stbl = trak['mdia']['minf']['stbl']
				stco = stbl['stco']['entry']	#Chunk Offset
				stsz = stbl['stsz']['entry']	#Sample Size
				stsc = stbl['stsc']['entry']	#Sample Count Per Chunk
				stss = stbl['stss']['entry']
				stts = stbl['stts']['entry']	#Sample Count PlayTime

				print self._parse(stts, timeoffset, duration, mdhd['timescale'])

			elif trak['mdia']['hdlr']['handler-type'] == 'soun':
				mdhd = trak['mdia']['mdhd']
				stbl = trak['mdia']['minf']['stbl']
				stco = stbl['stco']['entry']	#Chunk Offset
				stsz = stbl['stsz']['entry']	#Sample Size
				stsc = stbl['stsc']['entry']	#Sample Count Per Chunk
				stts = stbl['stts']['entry']	#Sample Count PlayTime

				print self._parse(stts, timeoffset, duration, mdhd['timescale'])

		return self

	def buffer(self):
		print 'buffer'


if __name__ == '__main__':
	TS('../../BigBuckBunny.mp4').segment(2, 10)
