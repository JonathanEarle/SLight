import socket

host='192.168.3.104'
#host='192.168.43.47'
port=5561

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
state=True
while state:
    try:
        s.connect((host,port))
        state=False
    except:
        print("could not connect yet")

#comm=input("enter cmd: ")
s.send(str("u"))

def rec():


    reply=s.recv(1024)  
    return reply

#s.close()


