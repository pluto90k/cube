import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4

mp4 = MP4('BigBuckBunny.mp4')
dic = mp4.dic()

atom = dic['atom']
for trak in atom['moov']['trak']:
    h = trak.get('mdia', {}).get('hdlr', {}).get('handler-type')
    stbl = trak.get('mdia', {}).get('minf', {}).get('stbl', {})
    
    stsc = stbl.get('stsc', {}).get('entry', [])
    stco = stbl.get('stco', {}).get('entry', [])
    stsz = stbl.get('stsz', {}).get('entry', [])
    print("Track: " + str(h))
    print("stsc len: " + str(len(stsc)))
    print("stco len: " + str(len(stco)))
    print("stsz len: " + str(len(stsz)))
    
    # Run the original logic to see if it breaks at boundary
    info = [] ; pos = 0
    count = stsc[pos]['sample_per_chunk']
    index = stsc[pos]['first_chunk_index']
    offset = stco[index - 1]['chunk_offset']
    
    # print first few samples
    for num in range(50):
        if num == count:
            pos += 1
            if pos < len(stsc) and index + 1 < stsc[pos]['first_chunk_index']: pos -= 1 ; index += 1
            elif pos < len(stsc): index = stsc[pos]['first_chunk_index']
            if index-1 < len(stco): offset = stco[index-1]['chunk_offset']
            if pos < len(stsc): count += stsc[pos]['sample_per_chunk']
        info.append({"offet": offset, "size": stsz[num]['entry_size']})
        offset += stsz[num]['entry_size']
        
    print("Generated first few info offsets:")
    for i in range(25):
        print("  Sample " + str(i) + " offset: " + str(info[i]['offet']))

    print("Expected chunks:")
    for i in range(5):
        print("  chunk " + str(i) + " offset: " + str(stco[i]['chunk_offset']))
    break
