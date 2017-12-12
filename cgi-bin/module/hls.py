#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4
from ts  import TS

class HLS(MP4):
	def __init__(self, file_name):
		super(HLS,self).__init__(file_name)
		self.fileName = file_name
		p = re.compile("(.+)\.(mp4)(.+)?")
		g = p.search(file_name)
		self.name = g.group(1)

	def m3u8(self):
		print "Content-type:application/vnd.apple.mpegurl\r\n"
		print "#EXTM3U\r\n"
		print "#EXT-X-TARGETDURATION:10\r\n"

		for i in range(0, 10):
			print "#EXTINF:11,\n"
			print "%s-%d.ts\n" % ( self.name, i )

		print "#EXT-X-ENDLIST\r\n"



