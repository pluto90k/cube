#!/usr/bin/env python

import cgi, re, json, sys, os
from module.hls import HLS
from module.mp4 import MP4

#JSON Print
def _json(data):
	print "Content-type: application/json\r\n"
	print(json.dumps(data))

#MP4 Stream Out
def _out(filename, chunk_size=1024):
	out_file = sys.stdout
	#head =  "Content-Type:application/octet-stream; name = \"%s\"\r\n" % filename
	head =  "Accept-Ranges:bytes\r\n"
	head +=  "Content-Type:video/mp4\r\n"
	head +=  "Content-Length:%ld\r\n" % os.stat(filename).st_size

	fo = open(filename, "rb")
	print head

	while True:
		out = fo.read(chunk_size)
		if out:
			out_file.write(out)
		else:
			break;

	fo.close()

form = cgi.FieldStorage()
fileName = form.getvalue('file')

p = re.compile("(.+)\.(mp4|json|m3u8|ts)(.+)?")
g = p.search(fileName)

data = {'error':'none', 'data':None}

if g:
	fileName = g.group(1)	    #FileName
	ext = g.group(2)  		#File extensions

	fileName = "%s.%s" % (fileName, 'mp4')

	if not os.path.exists(fileName):     #File Check
		data["error"] = "Unknown File"
		_json(data)
	elif ext == 'json':					#MediaInfo
		data["error"] = "none"
		data["data"] = MP4(fileName).dic()
		_json(data)
	elif ext == 'mp4':  				#Mp4Stream
		_out(fileName)
	elif ext == 'm3u8':  				#Http Live Streaming
		HLS(fileName).m3u8()
	elif ext == 'ts':
		#TODO :TS(fileName).out() convert
		seq = form.getvalue('seq')
		sec = form.getvalue('sec')
		#TS(fileName).segment(seq, sec).buffer()

else:
	data["error"] = "Unknown File"
	_json(data)
