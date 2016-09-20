import socket

host=''
port=5560

msg=[1,2,3]

def setupServer():
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print("Socket created")
	try:
		s.bind((host,port))
	except socket.error as msg:
		print(msg)
	print("Socket bind complete")
	return s

def setupConnection():
	s.listen(1)
	conn, addr=s.accept()
	print("Connected to: "+addr[0]+" :"+ str(addr[1]))
	return conn

def dataTransfer(conn):
#	data=conn.recv(1024)
	reply=msg
	conn.sendall(str(reply))
	print("Data has been sent")

s=setupServer()

while True:
	try:
		conn=setupConnection()
		dataTransfer(conn)
	except:
		print('Error')
		break	
