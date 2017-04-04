#import subprocess as sp
#FFMPEG_BIN = 'ffmpeg'
#command = [ FFMPEG_BIN,
#            '-i', 'udp://127.0.0.1:12345',
#            
#            'rtmp://']
#pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
import socket
import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode
import cPickle

m=11
k=16
window =28
#sequence =  list( {} for i in xrange(8) )
sequence = list(range(k) for i in xrange(window))
in_progress = list( 0 for i in xrange(window))
cur_send = 0
parity = list(range(m) for i in xrange(window))
par_progress = list(0 for i in xrange(window))

def receive_write_stream():
    UDP_IP = "127.0.0.1"
#    reconstruct_rtmp = librtmp.RTMP("rtmp://178.62.61.235:1935/show/stream_name", live=True)
#    reconstruct_rtmp.connect()
#    rtmpwritestream = reconstruct_rtmp.create_stream(True,True)
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    send_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, 5007))
    send_sock.connect((UDP_IP,5008))
    get_bytes(sock,send_sock)

def get_bytes(sock,send_sock):
    global k
    while True:
        data,addr = sock.recvfrom(5120)
        #rtmpwritestream.write(data) # This works perfectly
        if data:
            if len(data) > 5120:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            #print data
            #decode_from_fec(data,stream)
	    data = cPickle.loads(data)
            #data = tuple(data[0].split(','))
            if data[0][1] < k:
                decode_from_fec(send_sock,data[0][0],data[0][1],data[1])
            else:
                fill_parity(data[0][0],data[0][1],data[1])
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def fill_parity(frame,row,data):
    global k
    row= row -k
    global parity
    global par_progress
    global m
    if par_progress[frame]<m:
        if parity[frame][row] == row:
	    parity[frame][row] = data
            par_progress[frame]+=1
        else:
            parity[frame] = range(m)
            parity[frame][row] = data
            par_progress[frame] =1
    return

def try_decode(frame):
    global sequence
    global parity
    global in_progress
    global par_progress 
    global m
    global k
    print "try decode for frame" , frame , "  current queue status is ", in_progress
    if in_progress[frame]+ par_progress[frame] < k:
        print "decode failed becuase only have " , in_progress[frame]+ par_progress[frame] , "blocks instead of 16"
        return False
    else:
        blocks =[]
        for index,block in enumerate(sequence[frame]):
            if block!= index:
                blocks+=block
        #for index,parity in enumerate(parity[frame]):
        #    if parity!=index:
        #        blocks+=parity
        #print fec_decode(k,m,512,blocks)
        #print blocks   # TODO add back the blocks into sequnce to construct the frame here
        return True

def decode_from_fec(send_sock,frame,row,data):
    global sequence
    global in_progress
    global cur_send
    block_size =512
    global k 
    global window
    #print "recv", frame, row
    # wait for total decode
    if in_progress[frame]<k:
        if sequence[frame][row]==row:
            sequence[frame][row]= data
            in_progress[frame]+=1
            #print "added to frame ", frame, " block" , row
        else:
            if not try_decode(frame): # decode failed
                sequence[frame] = range(k)
                sequence[frame][row] = data
                in_progress[frame] =1
                cur_send = (cur_send+1)%window
    # if received all blocks
    for index in xrange(cur_send,window):
        if in_progress[index]==k:
            try:
                construct_rtmp(send_sock,sequence[index], index)
                sequence[index] = range(k)
                in_progress[index] = 0
                cur_send = (index+1)%window
            except IOError as e:
                print "I/O Error" , e
        else:
       #     if in_progress[(index+1)%8]==16 and in_progress[(index+2)%8]==16:
       #         sequence[index] = range(16)
       #         in_progress[index] =0
       #         cur_send = (index+1)%8
       #     else:
            return
	    
    
    # decode using below for row > k and check for frame 
    #decoded_data = fec_decode(k, m, block_size, blocks)
    #if decoded_data == 0:
    #    construct_rtmp(blocks,stream)


def construct_rtmp(send_sock,blocks, frame):
    """
    A client can publish a stream by calling RTMP_EnableWrite() before the RTMP_Connect() call, and then using RTMP_Write() after the session is established
    """
    global window
    data = bytearray()
    for block in blocks:
        data+=block
    send_sock.send(data)
    #stream.write(data)
    if frame !=window-1:
        print  frame,
    else: 
        print frame 

if __name__ == '__main__':
    receive_write_stream()
