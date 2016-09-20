import time
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

maxVehicles=10
vehicles = [None]*maxVehicles
vehiclesNum = 0

LEDMult=3 #The amount of LEDs associated with one sensor

LEDS = [16,12,17,27,5,6] #GPIO of LED
LEDsNum=len(LEDS) #Number of LEDS

Sensors = [23,18,24] #GPIO of sensor
sensorsNum=len(Sensors) #Number of Sensors

sensorTime=[None]*sensorsNum #Time at which the sensor was passed
sensorState=[None]*sensorsNum #Used to keep check of the exact point where the state changes from 0 to 1 which dictates exactly when the car first begins passing the sensor. 

#Used to keep check of what the new state is after the set of "stepThrough" functions are run, single element can be, 1 meaning light on, 0 meaning light off, or - meaning keep corresponding state of LEDsState
LEDsStateNew=[None]*LEDsNum
LEDsState=[None]*LEDsNum #Single element can be either 1 meaning light on or 0 meaning light off

#Setup Sensor GPIO Pins
for i in range(0,len(Sensors)):
        GPIO.setup(Sensors[i],GPIO.IN)

#Setup LED GPIO Pins
for i in range(0,len(LEDS)):
        GPIO.setup(LEDS[i],GPIO.OUT)

#Turns a light on
def lighton(i):
        GPIO.output(LEDS[i],GPIO.HIGH)
        
#Turns a light off
def lightoff(i):
        GPIO.output(LEDS[i],GPIO.LOW)

def checker(state):
        if state == 0:
                t = threading.Timer(2,lightoff,[Light])
                t.start()
            
#Function used to detect if input in being recieved on the motion sensor    
def scan(S):
	curr= GPIO.input(S)
	if curr ==0:
		return S	
	else: 	
		return 0

#Turns all the lights off
def resetLights():
        for i in range(0,6):
                lightoff(i)

#Function requests input of a LED number and lights it for two seconds for you to determine which LED is which, terminated by -1
def testLight():
        while 1:
                LED= input("Enter LED #: ")
                if LED==-1:
                        break
                if LED>=0 and LED <LEDsNum:
                        lighton(LED)
                        t = threading.Timer(2,lightoff,[LED])
                        t.start()

#Function continuously checks for an object passing any sensor, when an object has passed a sensor that particular sensor index is printed
def testSensor():
        initSensorState()
        while 1:
                #Keeps scanning for motion
		for i in range(0,sensorsNum):
                        state = scan(Sensors[i])
                        
                        if state and sensorState[i]==0:
                                print(i)
                                sensorState[i]=1
                        elif state and sensorState[i]==1:
                                sensorState[i]=1
                        elif state==0 and sensorState[i]==1:
                                sensorState[i]=0

def removeVehicle(pos):
        temp
        for i in range(pos+1,vehiclesNum):
                vehicles[i-1]=vehicles[i]
        vehiclesNum-=1
                
def addVehicle(vehicle):
        vehicles[vehiclesNum]=vehicle
        vehicles+=1
                
class vehicle:
        currentPos=0
        timePlaced=0
        stepThroughTime=0
        visionRange=0
        
        def __init__(self,currentPos,timePlaced,stepThroughTime,visionRange):
                 self .currentPos=currentPos
                 self.timePlaced=timePlaced
                 self.stepThroughTime=stepThroughTime
                 self.visionRange=visionRange

def calcStepThroughTime(timeDifference):
        return timeDifference/6

def calcVisionRange(timeDifference):
        return 1

def stepThrough():
        currentTime=time.clock()
        initLEDsStateNew()
        
        global vehiclesNum
        global vehicles
        
        for i in range(0,vehiclesNum):
                if vehicles[i].stepThroughTime+vehicles[i].timePlaced <currentTime:
                        #Change timeplaced and currentPosition
                        vehicles[i].timePlaced=vehicles[i].timePlaced+vehicles[i].stepThroughTime
                        vehicles[i].currentPos+=1

                        #Update LEDsStateNew
                        pos=vehicles[i].currentPos
                        leadingPos=pos+vehicles[i].visionRange
                        trailingPos=pos-vehicles[i].visionRange

                        if trailingPos>=LEDsNum:
                                #RemoveVehicle
                                vehiclesNum-=1
                                for x in range(i,vehiclesNum):
                                        vehicles[x]=vehicles[x+1]
                        
                        if(leadingPos<LEDsNum):#Trailing LED to leading LED must be changed to high
                                for i in range(trailingPos,leadingPos+1):
                                        LEDsStateNew[i]=1

                        trailingPos=trailingPos-1 #Two less characters
                        if(trailingPos>=0 and trailingPos<LEDsNum): #One LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                                if LEDsStateNew[trailingPos]=="-":
                                        LEDsStateNew[trailingPos]=0
                                elif LEDsStateNew[trailingPos]==1:
                                        LEDsStateNew[trailingPos]=1
                                else:
                                        LEDsStateNew[trailingPos]=0


def addVehicleStartingLEDs(currentPos,visionRange):
        for i in range(currentPos-visionRange,currentPos+visionRange+1):
                if i>=0 and i<LEDsNum:
                        LEDsState[i]=1

def updateStateNew():
        for i in range(0,LEDsNum):
                if LEDsStateNew[i]!="-":
                        LEDsState[i]=LEDsStateNew[i]
                
def turnOnLEDs():
        for i in range(0,LEDsNum):
                if LEDsState[i]:
                        lighton(i)
                else:
                        lightoff(i)

def initLEDsState():
        for i in range(0,LEDsNum):
                LEDsState[i]=0

def initLEDsStateNew():
        for i in range(0,LEDsNum):
                LEDsStateNew[i]="-"

def initSensorState():
        for i in range(0,sensorsNum):
                sensorState[i]=0

def main():
	try:
                resetLights()
                run =True

                #used for setting up which light and sensor goes to which physical location
                #testLight()
                #testSensor()

                initSensorState()
                initLEDsState()
                initLEDsStateNew()
		
		while run:
                        #Keeps scanning for motion
                        for i in range(0,sensorsNum):
                                state = scan(Sensors[i])
                                
                                if state and sensorState[i]==0:
                                        sensorTime[i]=time.clock() #The time which the sensor was triggered is stored
                                        sensorState[i]=1
                                                
                                        #Create new vehicle
                                        if i==1:#for demonstration purposes a new vehicle will be created when sensor[1] is triggered
                                                timeDifference=sensorTime[i]-sensorTime[i-1]
                                                veh=vehicle(0,sensorTime[i],calcStepThroughTime(timeDifference),calcVisionRange(timeDifference))

                                                #AddVehicle
                                                global vehicles
                                                global vehiclesNum
                                                vehicles[vehiclesNum]=vehicle(0,sensorTime[i],calcStepThroughTime(timeDifference),calcVisionRange(timeDifference))
                                                addVehicleStartingLEDs(vehicles[vehiclesNum].currentPos,vehicles[vehiclesNum].visionRange)
                                                vehiclesNum+=1
                                                
                                                
                                elif state and sensorState[i]==1:
                                        sensorState[i]=1
                                elif state==0 and sensorState[i]==1:
                                        sensorState[i]=0

                        #Turn on lights
                        stepThrough()
                        updateStateNew()
                        turnOnLEDs()
                                        
        except KeyboardInterrupt:
		run = False
	finally:
		GPIO.cleanup();

if __name__ == "__main__": 
	main()

