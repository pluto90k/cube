import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4

mp = MP4('BigBuckBunny.mp4')
dic = mp.dic()
atom = dic['atom']

for trak in atom['moov']['trak']:
    h = trak.get('mdia', {}).get('hdlr', {}).get('handler-type')
    stbl = trak.get('mdia', {}).get('minf', {}).get('stbl', {})
    
    stss = stbl.get('stss', {}).get('entry', [])
    ctts = stbl.get('ctts', {}).get('entry', []) # Check if B-frames exist
    print("Track: " + str(h))
    print("Has keyframes table (stss): " + str(len(stss) > 0))
    print("Has Composition offsets (ctts): " + (str(len(ctts)) if ctts else 'None'))
