import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
from io import BytesIO
FH = open('BigBuckBunny.mp4', 'rb')
# Find avcC box
FH.seek(0)
data = FH.read(1024*1024) # Read 1MB
idx = data.find('avcC')
if idx != -1:
    # avcC box header: size(4), type(4)
    # So index idx points to 'avcC'. Header started 4 bytes before.
    # The version and profile info are after 'avcC'
    # byte 0: version (1)
    # byte 1: profile (1)
    # byte 2: profile_compat (1)
    # byte 3: level (1)
    # byte 4: 111111 + lengthSizeMinusOne (2 bits)
    v = ord(data[idx+8]) # byte 4 after 'avcC'
    print("lengthSizeMinusOne bits:", bin(v))
    print("Actual lengthSize:", (v & 3) + 1)
