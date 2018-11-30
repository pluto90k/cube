#!/usr/bin/env python
#coding:utf-8
from io import BytesIO

#TS PARSER ( How To make ts format? )


def _hex(byte):
	bio = BytesIO(byte)
	txt = ''
	while True:
		s = bio.read(1)
		if s == '': break
		txt = txt + '%02X ' % int(ord(s))
	bio.close()
	return txt

FH = open('./ts/BigBuckBunny-3.ts', 'rb')

while True:
	s = FH.read(4)
	if s == '': break
	print _hex(s)
	s = FH.read(184)
	print _hex(s)
