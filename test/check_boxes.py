import sys
from io import BytesIO
def find_boxes(data, path=""):
    bio = BytesIO(data)
    while True:
        sz_raw = bio.read(4)
        if not sz_raw or len(sz_raw) < 4: break
        sz = int(sz_raw.encode('hex'), 16)
        tp = bio.read(4).decode('ascii', errors='ignore')
        if sz < 8: break
        print(path + "/" + tp + " (" + str(sz) + ")")
        if tp in ['moov', 'trak', 'mdia', 'minf', 'stbl']:
            find_boxes(bio.read(sz - 8), path + "/" + tp)
        else:
            bio.read(sz - 8)
FH = open('BigBuckBunny.mp4', 'rb')
find_boxes(FH.read(1024*1024))
