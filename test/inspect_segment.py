import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
from ts import TS
from io import BytesIO

mp = MP4('BigBuckBunny.mp4')
dic = mp.dic()
v_info = dic['atom']['moov']['trak'][0]['mdia']['minf']['stbl']['stsd']['entry'][0]['conf']
print("SPS Hex:", v_info.get('sps'))
print("PPS Hex:", v_info.get('pps'))

ts_obj = TS('BigBuckBunny.mp4')
bio = ts_obj.segment(0, 10).ts()
data = bio.getvalue()
print("Segment 0 size:", len(data))
print("First 16 bytes:", data[:16].encode('hex'))
# Try to find PAT
idx = data.find('\x47\x00\x00')
if idx != -1:
    print("PAT found at:", idx)
