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
def _bit_to_bytearray(data):
	out = []
	while data:
		(value, data) =  (lambda t, n : (t[0:n], t[n:]))(data, 8)
		out.append(int('0b' + value, base=2))
	return bytearray(out)

FH = open('./ts/BigBuckBunny-1.ts', 'rb')
count = 0
pat = ''
sdt = ''
pmt = ''
sdt_count = 0
org = False
while True:
	s = FH.read(4)
	if s == '': break
	#print _hex(s)
	if s[:3] == bytearray([0x47, 0x40, 0x11]):
		#print 'sdt [%s]' % _hex(s)
		print 'sdt {}'.format(sdt_count)
		s = FH.read(184)
		if not sdt:
			sdt = s
		elif sdt == s:
			pass
			#print 'sdt same'
		else:
			print _hex(s)
		#print ("{}".format(sdt_count))
		sdt_count = 0
		continue
	elif s[:3] == bytearray([0x47, 0x40, 0x00]):
		#print 'pat [%s]' % _hex(s)
		print 'pat'
		s = FH.read(184)
		if not pat:
			pat = s
		elif pat == s:
			pass
			#print 'pat same'
		else:
			print _hex(s)
		continue
	elif s[:3] == bytearray([0x47, 0x50, 0x00]):
		#print 'pmt [%s]' % _hex(s)
		print 'pmt {}'.format(count)
		s = FH.read(184)
		if not pmt:
			pmt = s
		elif pmt == s:
			pass
			#print 'pmt same'
		else:
			print _hex(s)
		#print ("{}".format(count))
		count = 0
		continue
	else:
		if s[:3] == bytearray([0x47, 0x41, 0x00]):	#Video
			org = True

		count += 1
		sdt_count += 1
		#print ("{}".format(count))

	data = FH.read(184)
	if org :
		if s[3:] >= bytearray([0x30]) and data[1:2] != bytearray([0xFF]) and '{:08b}'.format(int(ord(data[1:2])))[3:4] == '1':
			value = ''
			for b in data[2:8]:
				value += '{:08b}'.format(int(ord(b)))

			out = ' PCR [%d]' % int(value[:33], base=2)
			#print 'len %d %s' % (int('{:08b}'.format(int(ord(data[:1]))), base=2), _hex(data[int('{:08b}'.format(int(ord(data[:1]))), base=2) + 1:]))
			data = data[int('{:08b}'.format(int(ord(data[:1]))), base=2) + 1:]
			if  data[6:8] == bytearray([0x80, 0xC0]):
				pts = data[10:14]
				value = ''
				for b in pts:
					value += '{:08b}'.format(int(ord(b)))
				pts = int(value[:15] + value[16:-1], base=2)

				dts = data[15:19]
				value = ''
				for b in dts:
					value += '{:08b}'.format(int(ord(b)))

				dts = int(value[:15] + value[16:-1], base=2)
				out += ' PTS (%d), DTS (%d), GAP (%d)' % (pts, dts, pts - dts)
			elif data[6:8] == bytearray([0x80, 0x80]):
				pts = data[10:14]
				value = ''
				for b in pts:
					value += '{:08b}'.format(int(ord(b)))
				pts = int(value[:15] + value[16:-1], base=2)
				out += ' PTS (%d)' %  (pts)

			print out
		elif org:
			if data[:4] == bytearray([0x00, 0x00, 0x01, 0xE0]):
				#out = 'PES %s, %s' % (_hex(data[:6]), _hex(data[6:8]))
				out = ' PES'
				if  data[6:8] == bytearray([0x80, 0xC0]):
					pts = data[10:14]
					value = ''
					for b in pts:
						value += '{:08b}'.format(int(ord(b)))
					pts = int(value[:15] + value[16:-1], base=2)

					dts = data[15:19]
					value = ''
					for b in dts:
						value += '{:08b}'.format(int(ord(b)))

					dts = int(value[:15] + value[16:-1], base=2)
					out += ' PTS:%d, DTS:%d, GAP:%d' % (pts, dts, pts - dts)
				elif data[6:8] == bytearray([0x80, 0x80]):
					pts = data[10:14]
					value = ''
					for b in pts:
						value += '{:08b}'.format(int(ord(b)))
					pts = int(value[:15] + value[16:-1], base=2)
					out += ' PTS:%d' %  (pts)

				print out
			else:
				#out = 'A PES %s' % _hex(data[:6])
				out = ' A PES'
				data = data[int('{:08b}'.format(int(ord(data[:1]))), base=2) + 1:]
				if  data[6:8] == bytearray([0x80, 0xC0]):
					pts = data[10:14]
					value = ''
					for b in pts:
						value += '{:08b}'.format(int(ord(b)))
					pts = int(value[:15] + value[16:-1], base=2)

					dts = data[15:19]
					value = ''
					for b in dts:
						value += '{:08b}'.format(int(ord(b)))

					dts = int(value[:15] + value[16:-1], base=2)
					out += ' PTS:%d, DTS:%d, GAP:%d' % (pts, dts, pts - dts)
				elif data[6:8] == bytearray([0x80, 0x80]):
					pts = data[10:14]
					value = ''
					for b in pts:
						value += '{:08b}'.format(int(ord(b)))
					pts = int(value[:15] + value[16:-1], base=2)
					out += ' PTS:%d' %  (pts)
			#print _hex(data)

	org = False
