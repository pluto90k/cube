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

FH = open('./ts/BigBuckBunny-1.ts', 'rb')
for num in range(0, 100):
    print _hex(FH.read(4))
    print _hex(FH.read(184))
