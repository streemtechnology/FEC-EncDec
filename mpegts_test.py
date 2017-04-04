#import subprocess as sp
#FFMPEG_BIN = 'ffmpeg'
#command = [ FFMPEG_BIN,
#            '-i', 'rtmp://84.20.77.50/live/livestream1 live=1',
#            '-f', 'mpegts',
#            'udp://127.0.0.1:12345']
#pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)


import os, sys
from socket import socket, AF_INET, SOCK_DGRAM
import librtmp
from pylonghair import fec_encode, fec_decode
import cPickle

frame =0
k = 16
m =11
window=28

def get_stream():
    #conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
    #conn = librtmp.RTMP("rtmp://84.20.77.50/live/livestream1", live=True)
    #rtmpcall = conn.connect()
    #print "Transaction ID" , rtmpcall.transaction_id, "\n Result of the Call", rtmpcall.result()
    #rtmpstream = conn.create_stream()
    sock = socket(AF_INET,SOCK_DGRAM)
    sender_sock = socket(AF_INET,SOCK_DGRAM)
    sock.bind(('127.0.0.1',5006))# stream data
    sender_sock.connect(('127.0.0.1',5007))
    get_bytes(sock,sender_sock)

def get_bytes(sock,sender):
    global frame
    global window
    while True:
        data,addr = sock.recvfrom(8192)
        #rtmpwritestream.write(data) # This works perfectly
        #print "data ", len(data)
        if data:
            if len(data) > 8192:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            encode_to_fec(data,frame,sender)
            frame=(frame+1)%window
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def encode_to_fec(data,frame,sender):
    block_size = 512
    global k #= 16   # 512*16 = 8192 send all blocks of received data
    global m #= 4
    parity = bytearray(m * block_size)
    encoded_data = fec_encode(k, m, block_size, data, parity)
    if encoded_data == 0:
        #print "Encoded to FEC Data Bytes: "#, len(data), "Data Content:",  data
        blocks = []
        for row in range(k):
            offset = row * block_size
            block_data = data[offset:offset + block_size]
            blocks.append(( (frame,row), block_data))
        for row in range(m):
            offset = row * block_size
            block_data = parity[offset:offset + block_size]
            blocks.append(((frame,row+k),block_data))
            #print ((row,block_data))
        send_fec_data( blocks,sender)

def send_fec_data(blocks,sender):
   for block in blocks:
       #print len(block[1])
       sender.send(cPickle.dumps(block))
   #sock.send(parity)

if __name__ == '__main__':
    get_stream()
