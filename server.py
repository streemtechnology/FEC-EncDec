import socket
import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode
import cPickle

frame =range(8)
recv_count = 0
block_data = bytearray(16*512)

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
    global recv_count
    global block_data
    block_size =512
    k = 16
    
    # wait for total decode
    
    offset  = int(row)*block_size
    block_data[offset:offset+block_size] = data
    recv_count+=1
    #if recv_count ==0:
    #    block_data[offset:offset+block_size] = data
    #	recv_count+=1
    #else:
        # havent seen this block before
    #    block_data[offset:offset+block_size] = data
    #    recv_count+=1
        #if block_data[row]!=0:
	#    block_data[row:row+block_size] = data
	#    recv_count+=1
    # if received all blocks
    if recv_count == 16:
        recv_count =0
        try:
            stream.write(block_data)   
        except IOError as e:
            print "I/O error" , e                        
 
    
    # decode using below for row > k and check for frame 
    #decoded_data = fec_decode(k, m, block_size, blocks)
    #if decoded_data == 0:
    #    construct_rtmp(blocks,stream)


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
