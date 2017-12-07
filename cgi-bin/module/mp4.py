#!/usr/bin/env python
#coding:utf-8

import sys
import time
from io import BytesIO


class MP4(object):
	def __init__(self, file_name):
		self.fileName = file_name

	def _hex(self, byte):
		bio = BytesIO(byte)
		txt = ''
		while True:
			s = bio.read(1)
			if s == '': break
			txt = txt + '%02X' % int(ord(s))
		bio.close()
		return txt

	def _read(self, bio, dic):
		while True:
			size = bio.read(4)
			if size == '':break
			size = int(size.encode('hex'), 16)
			data = bio.read(size - 4)
			tp = data[:4].decode('utf-8')
			self._parser(tp, dic, data[4:])

	def _parser(self, name, dic, data):
		if name == 'moov': out = self._moov(data)
		elif name == 'mvhd': out = self._mvhd(data)
		elif name == 'trak': out = self._trak(data)
		elif name == 'mdia': out = self._media(data)
		elif name == 'mdhd': out = self._mdhd(data)
		elif name == 'minf': out = self._minf(data)
		elif name == 'hdlr': out = self._hdlr(data)
		elif name == 'vmhd': out = self._vmhd(data)
		elif name == 'dinf': out = self._dinf(data)
		elif name == 'dref': out = self._dref(data)
		elif name == 'stbl': out = self._stbl(data)
		elif name == 'stts': out = self._stts(data)
		elif name == 'stsd': out = self._stsd(data)
		elif name == 'stco': out = self._stco(data)
		elif name == 'stsz': out = self._stsz(data)
		elif name == 'stsc': out = self._stsc(data)
		elif name == 'mdat': out = {}
		else:out = {'data':self._hex(data)}

		if dic.has_key(name):
			if isinstance(dic[name], dict):dic[name]=[dic[name], out]
			else:dic[name].append(out)
		else:dic[name] = out
		return dic

	def _atom(self):
		FH = open(self.fileName, 'rb')
		dic = {}
		size = 4
		s = FH.read(size)
		l = int(s.encode('hex'), 16)

		while True:
			s = FH.read(l-size)
			head = s[:4].decode('utf-8')

			self._parser(head, dic, s[4:]) 

			s = FH.read(size)
			if s == '': break
			l = int(s[:4].encode('hex'), 16)

		FH.close()	
		return dic

	def _moov(self, moov):
		bio = BytesIO(moov)
		dic = {}
		self._read(bio, dic)
		bio.close()
		return dic

	def _mvhd(self, mvhd):
		bio = BytesIO(mvhd) 
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}
		
		s = 8 if dic['version'] else 4
		dic['create_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic['modification_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic['timescale']=int(bio.read(s).encode('hex'), 16) 
		dic['duration']=int(bio.read(s).encode('hex'), 16) 

		#Reserved
		bio.read(4) 
		bio.read(2) 
		bio.read(2) 
		bio.read(8) 
		bio.read(4 * 9) 
		bio.read(4 * 6)
		#--Reserved

		#A 32-bit integer that indicates a value to use for the track ID number of the next track added to this movie. Note that 0 is not a valid track ID value.
		dic['next-track-id'] = int(bio.read(4).encode('hex'), 16)
		bio.close()
		return dic

	def _tkhd(self, tkhd):
		bio = BytesIO(tkhd) 
		dic = {}
		head = bio.read(4).decode('utf-8')
		dic[head] = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}

		s = 8 if dic[head]['version'] else 4
		dic[head]['create_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic[head]['modification_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic[head]['track-id'] = int(bio.read(4).encode('hex'), 16)
		bio.read(4)
		dic[head]['duration']=int(bio.read(4).encode('hex'), 16)
		bio.read(4 * 3)
		bio.read(2)
		bio.read(2)
		bio.read(4 * 9)
		bio.read(4)
		bio.read(4)
		bio.close()
		return dic	

	def _trak(self, trak):
		bio = BytesIO(trak) 
		size = int(bio.read(4).encode('hex'), 16)
		tkhd = bio.read(size - 4)
		dic = self._tkhd(tkhd)		
		self._read(bio, dic)
		bio.close()
		return dic

	def _media(self, media):
		bio = BytesIO(media)
		dic = {}
		self._read(bio, dic)
		bio.close()
		return dic

	def _mdhd(self, mdhd):
		bio = BytesIO(mdhd)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}
		
		s = 8 if dic['version'] else 4
		dic['create_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic['modification_time']=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(bio.read(s).encode('hex'), 16)))
		dic['timescale']=int(bio.read(s).encode('hex'), 16) 
		dic['duration']=int(bio.read(s).encode('hex'), 16) 
		dic['language']='%s' % (bin(int(bio.read(2).encode('hex'), base=16))[2:17])
		bio.close()
		return dic

	def _minf(self, minf):
		bio = BytesIO(minf)
		dic = {}
		self._read(bio, dic)
		bio.close()	
		return dic

	def _hdlr(self, hdlr):
		bio = BytesIO(hdlr)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}
		bio.read(4)	#Reserved
		dic['handler-type']=bio.read(4).decode('utf-8') 
		bio.close()
		return dic

	def _vmhd(self, vmhd):
		bio = BytesIO(vmhd)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}
		bio.read(8) #Reserved
		bio.close()
		return dic

	def _dinf(self, dinf):
		bio = BytesIO(dinf)
		dic = {}
		self._read(bio, dic)
		bio.close()
		return dic

	def _dref(self, dref):
		bio = BytesIO(dref)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16)
		}

		count = int(bio.read(4).encode('hex'), 16) #Entry-Count

		dic['entry'] = []
		for i in range(0, count):	
			size = int(bio.read(4).encode('hex'), 16)
			data = bio.read(size)
			dic['entry'].append({
				'type':data[:4].decode('utf-8'),
				'version':int(data[4:5].encode('hex'), 16),
				'flag':int(data[5:8].encode('hex'), 16)
			})
		bio.close()
		return dic

	def _stbl(self, stbl):
		bio = BytesIO(stbl)
		dic = {}
		self._read(bio, dic)
		bio.close()	
		return dic

	def _stsd(self, stsd):
		bio = BytesIO(stsd)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16),
		}

		count = int(bio.read(4).encode('hex'), 16) #Entry-Count

		dic['entry'] = []
		for i in range(0, count):
			size = int(bio.read(4).encode('hex'), 16)
			data = bio.read(size)
			dic['entry'].append({
				'type':data[:4].decode('utf-8'),
				'width':int(data[28:30].encode('hex'), 16),	
				'height':int(data[30:32].encode('hex'), 16)
			})
		bio.close()
		return dic

	def _stts(self, stts):
		bio = BytesIO(stts)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16),
		}

		count = int(bio.read(4).encode('hex'), 16) #Entry-Count

		dic['entry'] = []
		for i in range(0, count):
			dic['entry'].append({
				'count':int(bio.read(4).encode('hex'), 16),
				'delta':int(bio.read(4).encode('hex'), 16)
			})

		bio.close()
		return dic	

	def _stsc(self, stsc):
		bio = BytesIO(stsc)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16),
		}

		count = bio.read(4) #Entry-count
		count = int(count.encode('hex'), 16)

		dic['entry'] = []
		for i in range(0, count):
			dic['entry'].append({
				'first_chunk_index':int(bio.read(4).encode('hex'), 16),
				'sample_per_chunk':int(bio.read(4).encode('hex'), 16),
				'sample_description_index':int(bio.read(4).encode('hex'), 16)
			})
		bio.close()
		return dic
	def _stco(self, stco):
		bio = BytesIO(stco)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16),
		}

		count = bio.read(4) #Entry-count
		count = int(count.encode('hex'), 16)
	
		dic['entry'] = []
		for i in range(0, count):
			dic['entry'].append({
				'chunk_offset':int(bio.read(4).encode('hex'), 16)
			})
		bio.close()
		return dic

	def _stsz(self, stsz):
		bio = BytesIO(stsz)
		dic = {
			'version':int(bio.read(1).encode('hex'), 16),
			'flag':int(bio.read(3).encode('hex'), 16),
			'sample_size':int(bio.read(4).encode('hex'), 16)
		}
	
		count = bio.read(4) #Sample-count
		count = int(count.encode('hex'), 16)
			
		dic['entry'] = []
		for i in range(0, count):
			size = bio.read(4).encode('hex')
			if size:
				size = int(size, 16)
				dic['entry'].append({
					'entry_size':size
				})
		bio.close()
		return dic

	def dic(self):
		return{
			"filename": self.fileName,
			"atom":self._atom()
		}

if __name__ == '__main__':
	MP4('../../Robotica.mp4').dic()

