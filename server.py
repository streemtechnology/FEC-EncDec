import socket
import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode

def receive_write_stream():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    reconstruct_rtmp = librtmp.RTMP("rtmp://178.62.61.235:1935/show/stream_name", live=True)
    reconstruct_rtmp.connect()
    rtmpwritestream = reconstruct_rtmp.create_stream(True,True)
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    sock1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    sock1.bind((UDP_IP, 5006))
    get_bytes(sock1,rtmpwritestream)

def get_bytes(sock1,stream):
    while True:
        data = sock1.recvfrom(512)
        #rtmpwritestream.write(data) # This works perfectly
        if data:
            if len(data) > 512:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            #decode_from_fec(data,stream)
            data = tuple(data[0].split(','))
            print data[0] , "   " , data[1]
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def decode_from_fec(blocks,stream):
    k = 16
    m = 4
    block_size = 512
    decoded_data = fec_decode(k, m, block_size, blocks)
    if decoded_data == 0:
        construct_rtmp(blocks,stream)


def construct_rtmp(blocks,stream):
    """
    A client can publish a stream by calling RTMP_EnableWrite() before the RTMP_Connect() call, and then using RTMP_Write() after the session is established
    """
    data = bytearray()
    for block in blocks:
        #print blocks, block
	data+=block[1]
        #rtmpwritestream.write(block[1])
        #print rtmpwritestream.write(block[0])
    stream.write(data)

if __name__ == '__main__':
    receive_write_stream()
