import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
mp = MP4('BigBuckBunny.mp4')
stsz = mp.dic()['atom']['moov']['trak'][0]['mdia']['minf']['stbl']['stsz']['entry']
print("First 10 sample sizes:", [s['entry_size'] for s in stsz[:10]])
