import socket
import pickle

host='192.168.1.2' #IP of host
port=5560 #Port Number


while True:
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	data=pickle.loads(s.recv(1024))
	print(data)
	s.close()
