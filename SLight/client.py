import socket

host='192.168.1.8'
port=5560

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((host,port))

#comm=input("enter cmd: ")
s.send(str("u"))

reply=s.recv(1024)
print(reply)

#s.close()

