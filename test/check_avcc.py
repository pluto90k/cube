import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
mp = MP4('BigBuckBunny.mp4')
stsd = mp.dic()['atom']['moov']['trak'][0]['mdia']['minf']['stbl']['stsd']['entry'][0]
conf = stsd.get('conf', {})
# avcC is at the end of the entry raw data
# But my parser puts it in 'conf'
# Let's see the raw data near avcC
print("Conf keys:", conf.keys())
