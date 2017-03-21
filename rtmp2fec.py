import os, sys
import librtmp
from pylonghair import fec_encode, fec_decode
# Create a connection


def get_stream():
    #conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
    conn = librtmp.RTMP("rtmp://84.20.77.50/live/livestream1", live=True)
    print conn.connect()
    print conn.__dict__
    stream = conn.create_stream()
    print stream
    get_bytes(stream)

def get_bytes(stream):
    while True:
        data = stream.read(9600)
        if data:
            if len(data) > 819:
                print "Cant handle more than 8192 bytes right now"
                sys.exit(0)
            encode_to_fec(data)
        else:
            print "Waiting for Data on the Stream"
            sys.exit(0)

def encode_to_fec(data):
    block_size = 8192
    k = 10
    m = 4
    parity = bytearray(m * block_size)
    encoded_data = fec_encode(k, m, block_size, data, parity)
    if encoded_data == 0:
        print "Encoded to FEC Data Bytes: ", len(data), "Data Content:",  data
        blocks = []
        for row in range(k):
            offset = row * block_size
            block_data = data[offset:offset + block_size]
            blocks.append((row, block_data))
        decode_from_fec(k, m, block_size, blocks)


def decode_from_fec(k, m, block_size, blocks):
    decoded_data = fec_decode(k, m, block_size, blocks)
    if decoded_data == 0:
        print "Decoded from FEC Data blocks: ", len(blocks), "Block content",  blocks

if __name__ == '__main__':
    get_stream()
