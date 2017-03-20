
import librtmp
from pylonghair import fec_encode, fec_decode
# Create a connection
conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
# Attempt to connect
conn.connect()
# Get a file-like object to access to the stream
stream = conn.create_stream()
k = 30
m = 6
block_size = 64
parity = bytearray(m * block_size)
data = 0
count =0
# Read 1024 bytes of data
while(count<1):
        data = stream.read(1024)
	print len(data)
        #cauchy_256_encode(k, m, data_ptrs, recovery_blocks, bytes)
        #_fec_encode(int k, int m, int block_size, unsigned char* data, unsigned char* parity)
        # 
        print fec_encode(k , m, block_size, data,parity)
        #for par in parity:
        #    print par
        count+=1
print len(parity)
blocks = []
for row in range(k-1):
        offset = row * block_size
        block_data = data[offset:offset + block_size]
        blocks.append((row, block_data))

blocks.append((k, bytearray(parity[:block_size])))
fec_decode(k, m, block_size, blocks)
print "*********************\n"

for x in blocks: print "**" ,x[1]

print "*********************\n"
print data
print "*********************\n"
