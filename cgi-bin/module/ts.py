#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4

class TS(MP4):
	def __init__(self, file_name):
		super(TS,self).__init__(file_name)
		self.fileName = file_name
	def segment(self, seq, duration):
		print (seq, duration)
		return self
	def buffer(self):
		print 'buffer'




if __name__ == '__main__':
	TS('../../BigBuckBunny.mp4').segment(0, 1).buffer()
