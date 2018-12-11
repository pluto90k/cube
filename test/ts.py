#!/usr/bin/env python
#coding:utf-8
from io import BytesIO

#TS PARSER ( How To make ts format? )
_PCR = 0
_VPTS = 0
_VDTS = 0
_APTS = 0
def bytes2int(str):
	return int(str.encode('hex'), 16)

def _hex(byte):
	bio = BytesIO(byte)
	txt = ''
	while True:
		s = bio.read(1)
		if s == '': break
		txt = txt + '%02X ' % int(ord(s))
	bio.close()
	return txt
def _bit_to_bytearray(data):
	out = []
	while data:
		(value, data) =  (lambda t, n : (t[0:n], t[n:]))(data, 8)
		out.append(int('0b' + value, base=2))
	return bytearray(out)

def _time(data):
	value = ''
	for b in data:
		value += '{:08b}'.format(int(ord(b)))
	return int(value[:15] + value[16:-1], base=2)

def _move(start, end, pos):
	return (start, end)

def _pcr_parser(adptF):
	data = adptF.read(6)
	value = ''
	for b in data:
		value += '{:08b}'.format(int(ord(b)))
	return int(value[:33], base=2)

def _pes_parser(body, pcr=None):
	global _PCR, _VPTS, _VDTS, _APTS
	_hex(body.read(3))		#PES	Prefix
	streamId = body.read(1)	#PES	Stream ID
	streamId = 'video' if streamId == bytearray([0xE0]) else 'audio'
	_hex(body.read(2))		#PES	Packet Length
	_hex(body.read(2))		#PES OPTION
	_hex(body.read(1))		#PES Header Length
	type = body.read(1)

	if pcr:
		print "PCR : [%d] | GAP [%d]" % (pcr, pcr - _PCR if _PCR != 0 else 0)
		_PCR = pcr

	if type == bytearray([0x21]):
		pts = body.read(4)
		pts = _time(pts)
		if streamId == 'audio':
			print "PTS : [%d] | GAP [%d] | [%s]" % (pts, pts - _APTS if _APTS != 0 else 0, streamId)		#only pts
			_APTS = pts
		else :
			print "PTS : [%d] | GAP [%d] | [%s]" % (pts, pts - _VPTS if _VPTS != 0 else 0, streamId)		#only pts
			_VPTS = pts

	elif type == bytearray([0x31]):
		pts = body.read(4)
		pts = _time(pts)
		type = body.read(1)
		dts = body.read(4)
		dts = _time(dts)
		if streamId == 'audio':
			print "PTS : [%d] | GAP [%d] | [%s]" % (pts, pts - _APTS if _APTS != 0 else 0, streamId)		#only pts
			_APTS = pts
		else :
			print "PTS : [%d] | DTS [%d] | VGAP [%d] | DGAP [%d] | [%s]" % (pts, dts, pts - _VPTS if _VPTS != 0 else 0, dts - _VDTS if _VDTS != 0 else 0, streamId),		#only pts
			print "(PTS-DTS) [%d] | (PTS-PCR) [%d] | (DTS-PCR) [%d]" % (pts - dts, pts - _PCR, dts - _PCR)		#only pts
			_VPTS = pts
			_VDTS = dts

def _ts_parser(head, body):
	body = BytesIO(body)
	if head[:3] == bytearray([0x47, 0x41, 0x00]):		#Video
		#print _hex(head)
		if head[3] >= bytearray([0x30]):				#Has Adaptation Field
			size = int('{:08b}'.format(int(ord(body.read(1)))), base=2)
			if size:
				adptF = BytesIO(body.read(size))
				if '{:08b}'.format(int(ord(adptF.read(1))))[3:4] == '1':#PCR
					_pes_parser(body, _pcr_parser(adptF))
				else:
					_pes_parser(body)
			else:
				_pes_parser(body)
		else:											#Original Feild
			_pes_parser(body)
	elif head[:3] == bytearray([0x47, 0x41, 0x01]):		#Audio
		#print _hex(head)
		if head[3] >= bytearray([0x30]):				#Has Adaptation Field
			size = int('{:08b}'.format(int(ord(body.read(1)))), base=2)
			_hex(body.read(size))
			_pes_parser(body)
		else:
			#print 'DATA'
			pass
	elif head[:3] == bytearray([0x47, 0x40, 0x11]):
		#print 'SDT'	#Service Description Table
		pass
	elif head[:3] == bytearray([0x47, 0x40, 0x00]):
		#print 'PAT'	#Program Association Table
		pass
	elif head[:3] == bytearray([0x47, 0x50, 0x00]):
		#print 'PMT'	#Program Map Table
		pass
	else:
		#print 'DATA'
		pass
FH = open('./ts/BigBuckBunny-1.ts', 'rb')
while True:
	head = FH.read(4)
	if head == '': break
	body = FH.read(184)
	_ts_parser(head, body)
