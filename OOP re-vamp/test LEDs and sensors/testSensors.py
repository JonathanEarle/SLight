import threading
import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO
GPIO.setmode(GPIO.BCM)

# Sets the GPIO Pins of the PI's sensors to send input to PI 
def setGPIOIn(sensors):
    for i in range(0,len(sensors)):
        GPIO.setup(sensors[i],GPIO.IN)

# Function used to detect if an object has passed the sensor or not
def scan(S): 
    curr= GPIO.input(S)
    # if curr !=0: # For python 3.5
    if curr ==0: # For python 2.7
        return S    
    else:     
        return 0

# function continuously checks for an object passing any sensor, when an object has passed a sensor that particular sensor index is printed on the terminal, This is used for setting up on the track
def testSensor(sensors,sensorsNum,sensorState):
    while True:
        for i in range(0,sensorsNum):
                state = scan(sensors[i]) # State of the sensor[i] passed
                
                if state and sensorState[i]==0: # Vehicle has begun passing the sensor
                    print(i)
                    sensorState[i]=1
                elif state and sensorState[i]==1: # vehicle is currently still passing the sensor
                    sensorState[i]=1
                elif state==0 and sensorState[i]==1: # vehicle has passed the sensor  fully, therefore reset sensorState[i] to 0
                    sensorState[i]=0
    
def main():
    sensors = [23,18]
    sensorsNum=len(sensors)
    sensorState=[0]*sensorsNum
    
    setGPIOIn(sensors)
    
    testSensor(sensors,sensorsNum,sensorState)
                    
if __name__ == "__main__": 
    main()
