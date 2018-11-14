#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4
from ts  import TS

class HLS(MP4):
	def __init__(self, file_name):
		super(HLS,self).__init__(file_name)
		self.fileName = file_name
		self.atom = self.dic()['atom']
		p = re.compile("(.+)\.(mp4)(.+)?")
		g = p.search(file_name)
		self.name = g.group(1)

	def m3u8(self, sec=10):
		timescale = self.atom['moov']['mvhd']['timescale']
		duration = self.atom['moov']['mvhd']['duration'] // timescale
		total = duration / sec, duration % sec
		
		if total[1] > 0:total = total[0] + 1
		else:total = total[0]

		print "Content-type:application/vnd.apple.mpegurl\r\n"
		print "#EXTM3U\r\n"
		print "#EXT-X-TARGETDURATION:%d\r\n" % (sec)

		for i in range(0, total):
			print "#EXTINF:%d,\n" % sec
			print "cube.py?file=%s.ts?seq=%d&sec=%d\n" % ( self.name, i, sec )

		print "#EXT-X-ENDLIST\r\n"

if __name__ == '__main__':
	HLS('../../BigBuckBunny.mp4').m3u8()
