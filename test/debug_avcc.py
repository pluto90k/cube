import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
from io import BytesIO

mp = MP4('BigBuckBunny.mp4')
with open('BigBuckBunny.mp4', 'rb') as f:
    data = f.read(500000) 
    idx = data.find(b'avcC')
    if idx != -1:
        print("avcC found at " + str(idx))
        avcc = data[idx+4:idx+4+10]
        len_size = (ord(avcc[4]) & 3) + 1
        print("lengthSizeMinusOne + 1 = " + str(len_size))
