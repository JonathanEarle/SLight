# Use of error handling(specifically error handling)
# accepts keyboard interrupt

import signal
import sys
import time

def signal_handler(signal, frame):
    print ('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print ('Press Ctrl+C')
while True:
    print("a")
    #time.sleep(1)