import socket

host='192.168.3.104'
#host='192.168.43.47'
port=5561

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

def dataTransfer(conn,msg):
#	data=conn.recv(1024)
	reply=msg
	conn.sendall(str(reply))
	print("Data has been sent")

s=setupServer()
conn=setupConnection()

def send(msg):
    global s

    #while True:
    try:
        
        dataTransfer(conn,msg)
    except:
        print('Error')
    #    break	
