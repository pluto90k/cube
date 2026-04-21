import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
mp = MP4('BigBuckBunny.mp4')
atom = mp.dic()['atom']
traks = atom['moov']['trak']
for i, trak in enumerate(traks):
    h = trak.get('mdia', {}).get('hdlr', {}).get('handler-type')
    stsz = trak['mdia']['minf']['stbl']['stsz']
    print("Track %d (%s) stsz count: %d" % (i, h, len(stsz.get('entry', []))))
    print("Track %d (%s) stsz sample_size field (skipped bytes):" % (i, h))
    # Let's check the sample_size field manually
    # We need to find the stsz box data again
