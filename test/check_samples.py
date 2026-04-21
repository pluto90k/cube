import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
mp = MP4('BigBuckBunny.mp4')
samples = mp._sampling(mp.dic()['atom']['moov']['trak'][0], 0, 1)
FH = open('BigBuckBunny.mp4', 'rb')
for s in samples[:5]:
    FH.seek(s['chunk_offset'])
    data = FH.read(s['sample_size'])
    # Header of first NALU
    sz = int(data[0:4].encode('hex'), 16)
    tp = ord(data[4]) & 0x1F
    print("Sample size: %d, First NALU size: %d, Type: %d" % (s['sample_size'], sz, tp))
