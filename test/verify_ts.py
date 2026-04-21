import sys
from io import BytesIO

def verify_nalus(data):
    # Find Annex-B start codes 00 00 00 01
    idx = 0
    while True:
        idx = data.find('\x00\x00\x00\x01', idx)
        if idx == -1: break
        idx += 4
        if idx < len(data):
            tp = ord(data[idx]) & 0x1F
            print("Found NALU at %d, type %d" % (idx-4, tp))
            # Find next start code to get size
            next_idx = data.find('\x00\x00\x00\x01', idx)
            if next_idx == -1: size = len(data) - idx
            else: size = next_idx - idx
            print("  Size: %d" % size)

# We need to extract the elementary stream from TS
def extract_es(ts_data, target_pid):
    es = bytearray()
    for i in range(0, len(ts_data), 188):
        pkt = ts_data[i:i+188]
        if len(pkt) < 188: break
        sync = pkt[0]
        if sync != '\x47': continue
        pid = ((ord(pkt[1]) & 0x1F) << 8) | ord(pkt[2])
        if pid != target_pid: continue
        
        pusi = (ord(pkt[1]) & 0x40) != 0
        afc = (ord(pkt[3]) & 0x30) >> 4
        pos = 4
        if afc & 2: # Has adaptation field
            af_len = ord(pkt[pos])
            pos += 1 + af_len
        
        if pos < 188:
            payload = pkt[pos:]
            if pusi:
                # PES header starts here. Let's skip it.
                # Skip 00 00 01 stream_id (3) + length (2) + flags (2) + header_len (1)
                # Then skip header_len
                pes_header_len = ord(payload[8])
                es += payload[9 + pes_header_len:]
            else:
                es += payload
    return es

with open('debug.ts', 'rb') as f:
    ts_data = f.read()
    video_es = extract_es(ts_data, 0x100)
    print("Video ES size: %d" % len(video_es))
    verify_nalus(str(video_es))
