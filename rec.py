import librtmp

# Create a connection
conn = librtmp.RTMP("rtmp://188.138.17.8:1935/albuk/albuk.stream", live=True)
# Attempt to connect
conn.connect()
# Get a file-like object to access to the stream
stream = conn.create_stream()
# Read 1024 bytes of data
while(True):
	data = stream.read(1024)

	print data
