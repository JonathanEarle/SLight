import socket
import pickle
import threading

host=''
serverIP='192.168.1.2' #IP of server to connect to, ie Next Pi
rport=5561
sport=5560 #Port number

#Data to be sent
one=1
two=2
data={"one":one,"two":two}

#Function to setup the server from which data will be retrieved
def setupServer():
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Socket created")
        try:
                s.bind((host,sport))
        except socket.error as msg:
                print(msg)
        print("Socket bind complete")
        return s

#Function which makes server waits for client to connect to it
def setupConnection():
        s.listen(1)
        conn, addr=s.accept()
        #print("Connected to: "+addr[0]+" :"+ str(addr[1]))
        return conn

#Function which sends the data to the client
def dataTransfer(conn):
        conn.sendall(pickle.dumps(data))
        #print("Data has been sent")

#Code which makes program act as a client too
def Client():
	while True:
		s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.connect((serverIP,rport))
		data=pickle.loads(s.recv(1024))
		print(data)
		s.close()

def Server():
	#Continuously loop through waiting for client to connect to server, sending the data and then waiting for data to change
	while True:
		try:	
		        conn=setupConnection()
		        dataTransfer(conn)
		
			one=input("Enter one: ")
			two=input("Enter two: ")
			data={"one":one,"two":two}		
		except:
		        print('Error')
		        break

s=setupServer() #Set up the server
threading.Thread(target=Server).start() #Start the server thread
strtClient=input("Start the client? ")
if strtClient==1:
	threading.Thread(target=Client).start()	#Start the client thread




