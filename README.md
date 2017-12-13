Python MP4 Streaming Server
===========================

VideoCube Blog
--------------

http://videocube.tistory.com
* * *


git clone https://github.com/pluto90k/cube.git

cd cube

python -m CGIHTTPServer 8000 .

root@linux-01:/data/cube> python -m CGIHTTPServer 8000 .

Serving HTTP on 0.0.0.0 port 8000 ...

### Media Info (JSON)

curl -i http://localhost:8000/cgi-bin/cube.py?file=BigBuckBunny.json

* * *

### MP4 (MPEG-4) Download

wget -O BigBuckBunny.mp4 http://localhost:8000/cgi-bin/cube.py?file=BigBuckBunny.mp4

* * *

### M3U8 (Http Live Streaming) Download

curl -i http://localhost:8000/cgi-bin/cube.py?file=BigBuckBunny.m3u8

* * *

### TS (Transport Stream) Download

wget -O BigBuckBunny(-([0-9]+)).ts http://localhost:8000/cgi-bin/cube.py?file=BigBuckBunny(-([0-9]+)).ts


### Nginx Proxy Setting
	location ~ \.(mp4|json|m3u8|ts)$ {
        rewrite ^/(.*) /cgi-bin/cube.py?file=$1 break;
        proxy_pass http://127.0.0.1:8000;
    }
