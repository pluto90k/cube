# cube
Python MP4 Streaming Server


git clone https://github.com/pluto90k/cube.git

cd cube

python -m CGIHTTPServer 8000 .

root@linux-01:/data/cube> python -m CGIHTTPServer 8000 .

Serving HTTP on 0.0.0.0 port 8000 ...


Media Info
curl -i http://localhost:8000/cgi-bin/cube.py?file=Robotica.json

MP4 Download
wget -O Robotica.mp4 http://localhost:8000/cgi-bin/cube.py?file=Robotica.mp4

Nginx Proxy

	location ~ \.(mp4|json)$ {
        rewrite ^/(.*) /cgi-bin/cube.py?file=$1 break;
        proxy_pass http://127.0.0.1:8000;
    }
