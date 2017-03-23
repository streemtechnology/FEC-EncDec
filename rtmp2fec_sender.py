import os, sys
from socket import socket, AF_INET, SOCK_DGRAM
import librtmp
from pylonghair import fec_encode, fec_decode

def get_stream():
    #conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
    conn = librtmp.RTMP("rtmp://84.20.77.50/live/livestream1", live=True)
    rtmpcall = conn.connect()
    print "Transaction ID" , rtmpcall.transaction_id, "\n Result of the Call", rtmpcall.result()
    rtmpstream = conn.create_stream()
    sock = socket(AF_INET, SOCK_DGRAM)
    sock1 = socket(AF_INET,SOCK_DGRAM)
    sock.connect(('127.0.0.1', 5005))#parity data
    sock1.connect(('127.0.0.1',5006))# stream data
    get_bytes(rtmpstream,sock,sock1)

def get_bytes(stream,sock,sock1):
    while True:
        data = stream.read(8192)
        #rtmpwritestream.write(data) # This works perfectly
        if data:
            if len(data) > 8192:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            encode_to_fec(data,sock,sock1)
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def encode_to_fec(data,sock,sock1):
    block_size = 512
    k = 16   # 512*16 = 8192 send all blocks of received data
    m = 4
    parity = bytearray(m * block_size)
    encoded_data = fec_encode(k, m, block_size, data, parity)
    if encoded_data == 0:
        print "Encoded to FEC Data Bytes: "#, len(data), "Data Content:",  data
        blocks = []
        for row in range(k):
            offset = row * block_size
            block_data = data[offset:offset + block_size]
            blocks.append((row, block_data))
        send_fec_data( parity, blocks,sock,sock1)

def send_fec_data(parity,blocks,sock,sock1):
   for block in blocks:
       sock1.send(str(block))
   #sock.send(parity)

if __name__ == '__main__':
    get_stream()
