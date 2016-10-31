import threading
import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO
GPIO.setmode(GPIO.BCM)

# Sets the GPIO Pins of the PI's LEDs to receive output from the PI 
def setGPIOOut(LEDS):
    for i in range(0,len(LEDS)):
        GPIO.setup(LEDS[i],GPIO.OUT)

# Turns on associated Light by the index number passed 
def lighton(LEDS,i):
        GPIO.output(LEDS[i],GPIO.HIGH)

# Turns off associated Light by the index number passed
def lightoff(LEDS,i):
        GPIO.output(LEDS[i],GPIO.LOW)

# Requests input of a LED number in the terminal and lights it for two seconds for u to determine which LED is which, terminate function by inputting "-1", This is used for setting up on the track
def testLight(LEDS,LEDsNum):
    while True:
        LED= input("Enter LED #: ") # For python 2.7
        #LED=int(input("Enter LED #: ")) # For python 3.5
        if LED==-1: # Terminating Condition
            break
        if LED>=0 and LED <LEDsNum: 
            lighton(LEDS,LED)
            t = threading.Timer(2,lightoff,[LEDS,LED]) # A thread is created with a timer of 2 seconds to turn off that light that was turned on
            t.start()

def main():
    LEDS = [16,12,17,27,5,20,19,21]
    LEDsNum=len(LEDS)
    
    setGPIOOut(LEDS)
    
    testLight(LEDS,LEDsNum)
            

            
if __name__ == "__main__": 
    main()
