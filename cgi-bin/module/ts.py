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

	def _bit_to_bytearray(self, data):
		out = []
		while data:
			(value, data) =  (lambda t, n : (t[0:n], t[n:]))(data, 8)
			out.append(int('0b' + value, base=2))
		return bytearray(out)

	def _AUD(self, data):
		###############################################
		# AccessUnitDelimeter
		###############################################
		#HEAD (4Byte) Length | DATA
		#00 00 00 01 09 F0 00 00 00 01
		nal = b'\x00\x00\x00\x01'
		data = nal + data[4:]
		head = b'\x00\x00\x00\x01\x09\xF0'
		data = head + data
		return data


	def _ADTS(self, data):
		###############################################
		# AudioDataTransportStream
		###############################################
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

		data = self._bit_to_bytearray(adts) + data
		return data

	def _SDT(self):
		###############################################
		# Service Description Table
		###############################################
		sdt = '{:08b}'.format(0x00) 		#start_session
		sdt += '{:08b}'.format(0x42)		#table_id
		sdt += '1'							#section_syntax_indicator
		sdt += '1'							#reserved_future_use
		sdt += '11'							#reserved

		body = '{:016b}'.format(0x0001)		#transport_stream_id
		body += '11'						#reserved
		body += '00000'						#version_number
		body += '1'							#current_next_indicator
		body += '{:08b}'.format(0x00)		#section_number
		body += '{:08b}'.format(0x00)		#last_section_number
		body += '{:016b}'.format(0xFF01)	#original_network_id
		body += '{:08b}'.format(0xFF)		#reserved_future_use
		body += '{:016b}'.format(0x0001)	#service id
		body += '111'						#reserved_future_use
		body += '111'						#EIT_user_defined_flags
		body += '0'							#EIT_schedule_flags
		body += '0'							#EIT_present_following_flags
		body += '100'						#running_status
		body += '0'							#free_CA_mode

		body = self._bit_to_bytearray(body)

		descriptor_tag = b'\x48'			#descriptor_tag
		service_type = b'\x01'
		service_provider_name = 'FFmpeg'
		service_provider_name = bytearray(service_provider_name)
		service_provider_name = bytearray([len(service_provider_name)]) + service_provider_name

		service_name = 'Service01'
		service_name = bytearray(service_name)
		service_name = bytearray([len(service_name)]) + service_name

		desc_body = service_type + service_provider_name + service_name
		desc_body_len = bytearray([len(desc_body)])

		descriptor = descriptor_tag + desc_body_len + desc_body
		descriptors_len = bytearray([len(descriptor)])

		descriptor = descriptors_len + descriptor

		crc_32 = b'\x77\x7C\x43\xCA'

		body = body + descriptor + crc_32

		sdt += '{:012b}'.format(len(body))
		sdt = self._bit_to_bytearray(sdt)

		sdt = sdt + body
		return sdt

	def _PAT(self, pmt_num = 4096):
		###############################################
		# Program Association Table
		###############################################
		pat = '{:08b}'.format(0x00) 		#start_session
		pat += '{:08b}'.format(0x00)		#table_id
		pat += '1'							#section_syntax_indicator
		pat += '0'							#'0'
		pat += '11'							#reserved

		body = '{:016b}'.format(0x0001)		#transport_stream_id
		body += '11'						#reserved
		body += '00000'						#version_number
		body += '1'							#current_next_indicator
		body += '{:08b}'.format(0x00)		#section_number
		body += '{:08b}'.format(0x00)		#last_section_number
		body += '{:016b}'.format(0x0001)	#program_number
		body += '111'						#reserved
		body += '{:013b}'.format(pmt_num)	#program_number

		body = self._bit_to_bytearray(body)

		crc_32 = b'\x2A\xB1\x04\xB2'
		body = body + crc_32

		pat += '{:012b}'.format(len(body))	#session_length
		pat = self._bit_to_bytearray(pat)

		pat = pat + body
		return pat

	def _PMT(self, pcr_pid = 0x100, video_pid = 0x100, audio_pid = 0x101):
		###############################################
		# Program MAP Table
		###############################################
		pmt = '{:08b}'.format(0x00) 		#start_session
		pmt += '{:08b}'.format(0x02)		#table_id
		pmt += '1'							#section_syntax_indicator
		pmt += '0'							#'0'
		pmt += '11'							#reserved

		body = '{:016b}'.format(0x0001)		#program_number
		body += '11'						#reserved
		body += '00000'						#version_number
		body += '1'							#current_next_indicator
		body += '{:08b}'.format(0x00)		#section_number
		body += '{:08b}'.format(0x00)		#last_section_number
		body += '111'						#reserved
		body += '{:013b}'.format(pcr_pid)	#PCR_PID
		body += '1111'						#reserved
		body += '{:012b}'.format(0)			#program_info_length

		body += '{:08b}'.format(0x1B)		#stream_type
		body += '111'						#reserved
		body += '{:013b}'.format(video_pid)	#ES PID
		body += '1111'						#reserved
		body += '{:012b}'.format(0)			#es_info_length

		body += '{:08b}'.format(0x0F)		#stream_type
		body += '111'						#reserved
		body += '{:013b}'.format(audio_pid)	#ES PID
		body += '1111'						#reserved

		descriptor_tag = bytearray([0x0A])
		descriptor = 'eng'
		descriptor = bytearray(descriptor) + b'\x00'
		descriptors_len = bytearray([len(descriptor)])
		descriptor = descriptor_tag + descriptors_len + descriptor

		body += '{:012b}'.format(len(descriptor))	#es_info_length
		body = self._bit_to_bytearray(body)
		body += descriptor

		crc_32 = b'\x8D\x82\x9A\x07'
		body = body + crc_32

		pmt += '{:012b}'.format(len(body))			#session_length
		pmt = self._bit_to_bytearray(pmt)

		pmt = pmt + body
		return pmt

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
	#TS('../../BigBuckBunny.mp4').segment(0, 10).ts()
	TS('../../BigBuckBunny.mp4')._PMT()
