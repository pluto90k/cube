import sys
sys.path.append('cgi-bin/module')
from ts import TS
ts_obj = TS('BigBuckBunny.mp4')
data = ts_obj.segment(0, 10).ts().getvalue()
with open('debug.ts', 'wb') as f:
    f.write(data)
