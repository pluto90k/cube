#!/usr/bin/env python
#coding:utf-8

import re
from mp4 import MP4

class TS(MP4):
	def __init__(self, file_name):
		super(TS,self).__init__(file_name)
		self.fileName = file_name

	def _readFS(self, FH, offset, size):
		FH.seek(offset)
		data = FH.read(size)
		return data

	#AccessUnitDelimeter
	#HEAD (4Byte) Length | DATA
	#00 00 00 01 09 F0 00 00 00 01
	def _AUD(self, data):
		nal = b'\x00\x00\x00\x01'
		data = nal + data[4:]
		head = b'\x00\x00\x00\x01\x09\xF0'
		data = head + data
		return data

	#AudioDataTransportStream
	def _ADTS(self, data):
		# --------------------------------------------
		# 1111 1111
		# -------------------------------------------- FF
		# 1111
		#fix = bytes(hex(int('0b111111111111', base=2)))

		# 0	 	MPEG-4 ( 0 ) MPEG-2 ( 1 )
		# 00 	layer always 0
		# 1  	protection absent, Warning, set to 1 if there is no CRC and 0 if there is CRC
		# -------------------------------------------- F1
		# 01 	profile, 00 Main 01 LC 10 SSR 11 AAC TP
		# 01 00 MPEG-4 Sampling Frequency Index ( 15 is forbidden )
		# 0		private bit
		# 0 10	channel_configuration
		# 0		originality
		# 0		home
		# 0		copyright_identification_bit
		# 0		copyright_identification_start
		# 00 0001 1101 000 aac_frame_length ( 13 )
		# 1 1111 1111 11   adts_buffer_fullness (11)
		# 00	no_raw_data_blocks_inframe		(2)
		# none CRC ( cyclic redundancy check protection absent is 0 => 16 )
		#FF F1 50 80 04 3F FC DE 04 00 00 6C 69 62 66 61 61 63 20 31 2E 32 38 00 00 42 00 93 20 04 32 00 47 ( 7 + 26 byte )
		#         50           80 04 3F FC
		#01 0100 0 010 0 0 0 0 00 0000 0100 001 11111111111 00 ( 33 )
		#1111 1111
		#0000 0010
		adts = '111111111111'		#(12)
		_len = len(data) + 7
		_type = '0' #MPEG-4 (0), MPEG-2 (1)
		_len = '{:013b}'.format(_len)
		_channel = '{:03b}'.format(2)
		_profile = '{:02b}'.format(1)
		_sampling_frequency_index = '{:04b}'.format(4)

		layer = '00'
		protection_absent = '1'
		private = '0'
		originality = '0'
		home = '0'
		copyright_identification_bit = '0'
		copyright_identification_start = '0'
		adts_buffer_fullness = '11111111111'
		no_raw_data_blocks_inframe = '00'

		adts += _type
		adts += layer
		adts += protection_absent
		adts += _profile
		adts += _sampling_frequency_index
		adts += private
		adts += _channel
		adts += originality
		adts += home
		adts += copyright_identification_bit
		adts += copyright_identification_start
		adts += _len
		adts += adts_buffer_fullness
		adts += no_raw_data_blocks_inframe

		out = []
		while adts:
			(value, adts) =  (lambda t, n : (t[0:n], t[n:]))(adts, 8)
			out.append(int('0b' + value, base=2))

		#data = bytearray(out) + data

		print self._hex(bytearray(out))
		return data

	def segment(self, seq, duration):
		timeoffset = seq * duration
		self.sample = self._sample(timeoffset, duration)
		return self

	def ts(self):
		FH = open(self.fileName, 'rb')
		while self.sample['video'] or self.sample['audio']:
			if self.sample['video']:
				sample = self.sample['video'].pop(0)
				offset = sample['chunk_offset']
				size = sample['sample_size']
				data = self._AUD(self._readFS(FH, offset, size))

			if self.sample['audio']:
				sample = self.sample['audio'].pop(0)
				offset = sample['chunk_offset']
				size = sample['sample_size']
				print "\n"
				print (sample['id'])
				data = self._ADTS(self._readFS(FH, offset, size))
				print self._hex(data)

		return
	def buffer(self):
		print 'buffer'

if __name__ == '__main__':
	TS('../../BigBuckBunny.mp4').segment(0, 10).ts()
