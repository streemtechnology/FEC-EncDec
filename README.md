# FEC-EncDec


sudo pip install python-librtmp

## Ubuntu 

apt-get install librtmp-dev libffi-dev


## Pylonghair 

* https://github.com/sampot/pylonghair
* https://github.com/rbit/pydtls


## Installation

* python setup.py install


## mpeg-ts usage 

* Start python mpegts\_recv.py
* Start python mpegts\_test.py
* Start ffmpeg -i "udp://127.0.0.1:5008" -f flv  rtmp://127.0.0.1/show/stream\_name
* Start  ffmpeg -i "rtmp://84.20.77.50/live/livestream1 live=1" -f mpegts udp://127.0.0.1:5006
* Stream at http://127.0.0.1:8080/hls/stream\_name.m3u8
