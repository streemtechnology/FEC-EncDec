import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock1 = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
sock1.bind((UDP_IP, 5006))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data1, addr = sock1.recvfrom(1024) # buffer size is 1024 bytes
    print "received message:", len(data) ," rec msg 1" ,len(data1)
