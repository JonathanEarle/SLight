import socket

host='192.168.1.6'
port=5560

while True:
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))

	reply=s.recv(1024)
	print(reply)

	s.close()
