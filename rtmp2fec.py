import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode

rtmpwritestream = 0

def write_stream():
    global rtmpwritestream
    reconstruct_rtmp = librtmp.RTMP("rtmp://178.62.61.235:1935/show/stream_name", live=True)
    reconstruct_rtmp.connect()
    rtmpwritestream = reconstruct_rtmp.create_stream(True,True)

def get_stream():
    #conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
    conn = librtmp.RTMP("rtmp://84.20.77.50/live/livestream1", live=True)
    rtmpcall = conn.connect()
    print "Transaction ID" , rtmpcall.transaction_id, "\n Result of the Call", rtmpcall.result()
    rtmpstream = conn.create_stream()
    write_stream()
    get_bytes(rtmpstream)

def get_bytes(stream):
    while True:
        data = stream.read(8192)
        #rtmpwritestream.write(data) # This works perfectly
        if data:
            if len(data) > 8192:
                print "Cant handle more than 8192 bytes right now, Got bytes: ", len(data)
                sys.exit(0)
            encode_to_fec(data)
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def encode_to_fec(data):
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
        decode_from_fec(k, m, block_size, blocks, data)


def decode_from_fec(k, m, block_size, blocks, data):
    decoded_data = fec_decode(k, m, block_size, blocks)
    if decoded_data == 0:
        print "Decoded from FEC Data blocks: "#, len(blocks), "Block content",  blocks
        if check_decode_success(blocks,data, block_size)==False:
	    print "Error Decoding FEC data"
	    sys.exit(0)
        print "Sending to reconstruct rtmp: "
        construct_rtmp(blocks)


def check_decode_success(blocks, data, block_size):
    offset = 0
    for block in blocks:
	if block[1] != data[offset:offset+block_size]:
            return False
        offset = offset+block_size
    return True


def construct_rtmp(blocks):
    """
    A client can publish a stream by calling RTMP_EnableWrite() before the RTMP_Connect() call, and then using RTMP_Write() after the session is established
    """
    for block in blocks:
        #print blocks, block
        rtmpwritestream.write(block[1])
        #print rtmpwritestream.write(block[0])
    #rtmpwritestream.write(blocks)

if __name__ == '__main__':
    get_stream()
