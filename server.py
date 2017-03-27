import socket
import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode
import cPickle

#sequence =  list( {} for i in xrange(8) )
sequence = list(range(16) for i in xrange(8))
in_progress = list( 0 for i in xrange(8))
cur_send = 0

def receive_write_stream():
    UDP_IP = "127.0.0.1"
    reconstruct_rtmp = librtmp.RTMP("rtmp://178.62.61.235:1935/show/stream_name", live=True)
    reconstruct_rtmp.connect()
    rtmpwritestream = reconstruct_rtmp.create_stream(True,True)
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, 5006))
    get_bytes(sock,rtmpwritestream)

def get_bytes(sock,stream):
    while True:
        data,addr = sock.recvfrom(5120)
        #rtmpwritestream.write(data) # This works perfectly
        if data:
            if len(data) > 5120:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            #decode_from_fec(data,stream)
	    data = cPickle.loads(data)
            #data = tuple(data[0].split(','))
            decode_from_fec(data[0][0],data[0][1],data[1],stream)
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def decode_from_fec(frame,row,data,stream):
    global sequence
    global in_progress
    global cur_send
    block_size =512
    k = 16
    #print "recv", frame, row
    # wait for total decode
    if in_progress[frame]<16:
        sequence[frame][row]= data
        in_progress[frame]+=1
        print "added to frame ", frame, " block" , row

    # if received all blocks
    for index in xrange(cur_send,8):
        if in_progress[index]==16:
            try:
                construct_rtmp(sequence[index],stream, index)
                sequence[index] = range(16)
                in_progress[index] = 0
                cur_send = (index+1)%8
            except IOError as e:
                print "I/O Error" , e
        else:
            return
	    
    
    # decode using below for row > k and check for frame 
    #decoded_data = fec_decode(k, m, block_size, blocks)
    #if decoded_data == 0:
    #    construct_rtmp(blocks,stream)


def construct_rtmp(blocks,stream, frame):
    """
    A client can publish a stream by calling RTMP_EnableWrite() before the RTMP_Connect() call, and then using RTMP_Write() after the session is established
    """
    data = bytearray()
    for block in blocks:
        data+=block
    stream.write(data)
    print "wrote frame" , frame

if __name__ == '__main__':
    receive_write_stream()
