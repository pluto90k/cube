import sys
sys.path.append('cgi-bin/module')
from mp4 import MP4
mp = MP4('BigBuckBunny.mp4')
dic = mp.dic()
audio_info = dic['data'].get('audio', {}).get('info', {})
video_info = dic['data'].get('video', {}).get('info', {})
print("Audio Info:", audio_info)
print("Video Info:", video_info)
