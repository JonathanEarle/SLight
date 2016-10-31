import signal
import sys
import threading
import time

def infiniteThread(run):
    while(run):
        print("b")

def infiniteThread2(run):
    while(run):
        a=1
        
run =True

def signal_handler(signal, frame):
    global run
    print ('You pressed Ctrl+C!')
    run=False


def main():
    a=signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        print("a")
        print(signal.getsignal(a))
    
    t = threading.Thread(target=infiniteThread, args=(run,))
    t.start()
    
    #t = threading.Thread(target=infiniteThread2, args=(run,))
    #t.start()
    
    #t = threading.Thread(target=keyboardInterruptHandler, args=(run,))
    #t.start()

if __name__ == "__main__": 
    main()