#add pi to pi communication to lines: ??(pass lights ahead to light) 167(pass vehicle to leading pi), 222(pass expectedSensorTime), 271(Retrieve last sensorTime from the previous pi)

import os
import pickle
import time
import threading
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

vehicles = []

LEDS = [16,12,17,27,5,20]#GPIO of LED
#Sensors = [23,18,24]#GPIO of sensor
Sensors = [23,18]


#testing LEDs and sensorsDistance
#LEDS = [15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3]#20 LEDS
#Sensors = [14,25,20,6,22]#5snesors

LEDsMult=int(len(LEDS)/len(Sensors)) #How many LEDs associate with one sensor
sensorsNum=len(Sensors)
sensorTime=[0]*sensorsNum#time at which the sensor was passed
sensorState=[0]*sensorsNum#used to keep check of the exact point where the state changes from 0 to 1 which dictates exactly when the car first begins passing the sensor. 
expectedSensorPass=[-1]*sensorsNum #Where index referencs the related sensor and the value referencsthe vehicle index number

LEDsNum=len(LEDS)
LEDsStateNew=[0]*LEDsNum#used to keep check of what the new state is after the set of "stepThrough" functions are run,single element can be, 1 meaning light on, 0 meaning light off, or - meaning keep corresponding state of LEDsState
LEDsState=[0]*LEDsNum#single element can be either 1 meaning light on or 0 meaning light off

LEDsDistance=[] #Distance from one sensor to another sensor
sensorsDistance=[] #Distance from one LED to another LED


for i in range(0,len(Sensors)):
        GPIO.setup(Sensors[i],GPIO.IN)

for i in range(0,len(LEDS)):
        GPIO.setup(LEDS[i],GPIO.OUT)

        
def setAllLEDsDistance():
    for i in range(0,len(Sensors)):
        if i==0:
            dist=sensorsDistance[i]
            avg=dist/LEDsMult
        else:
            dist=sensorsDistance[i]
            avg=dist/LEDsMult
        
        for j in range(i*LEDsMult,((i+1)*LEDsMult)):
            LEDsDistance.append(avg)
        
def setAllSensorsDistance(distance):
    for i in range(0,len(Sensors)):
        sensorsDistance.append(distance)

def printLEDsDistance():
    for i in range(0,len(LEDsDistance)):
        print(LEDsDistance[i])
        
def printSensorsDistance():
    for i in range(0,len(Sensors)):
        print(sensorsDistance[i])
        
def lighton(i):
        GPIO.output(LEDS[i],GPIO.HIGH)

def lightoff(i):
        GPIO.output(LEDS[i],GPIO.LOW)

def checker(state):
        if state == 0:
                t = threading.Timer(2,lightoff,[Light])
                t.start()

def scan(S): #Function used to detect if input in being recieved on the motion sensor
    curr= GPIO.input(S)
    if curr ==0:
        return S    
    else:     
        return 0
                
def resetLights():
        for i in range(0,LEDsNum):
                lightoff(i)
                

def testLight():#function requests input of a LED number and lights it for two seconds for u to determine which LED is which, terminate function by inputting "-1"
        while 1:
                LED= input("Enter LED #: ")
                if LED==-1:
                        break
                if LED>=0 and LED <LEDsNum:
                        lighton(LED)
                        t = threading.Timer(2,lightoff,[LED])
                        t.start()

def testSensor():#function continuously checks for an object passing any sensor, when an object has passed a sensor that particular sensor index is printed on the terminal. This function did not have a end function implimentation therefore ctrl+C
        initSensorState()
        
        while 1:
                #Keeps scanning for motion
                for i in range(0,sensorsNum):
                    	state = scan(Sensors[i])
                    	#print(state)
                	if state and sensorState[i]==0:
                    		print(i)
                    		sensorState[i]=1
                	elif state and sensorState[i]==1:
                    		sensorState[i]=1
                	elif state==0 and sensorState[i]==1:
                    		sensorState[i]=0
                
        

def vehicle(CurrentPos,TimePlaced,Speed,VisionRange):
        temp={"currentPos": CurrentPos, "timePlaced": TimePlaced, "speed": Speed, "visionRange": VisionRange}
        return temp

def calcStepThroughTime(speed,currentPos):
        return LEDsDistance[currentPos]/speed

def calcVisionRange(timeDifference):
        return 1

def stepThrough():
        currentTime=time.clock()
        for i in range(0,len(vehicles)):
                if vehicles[i]["speed"]!=-1:
                    if vehicles[i]["currentPos"]<LEDsNum:
                        stepThroughTime=calcStepThroughTime(vehicles[i]["speed"],vehicles[i]["currentPos"])
                    
                    
                        if stepThroughTime+vehicles[i]["timePlaced"] <currentTime:
                                #change timeplaced and currentPosition
                                vehicles[i]["timePlaced"]=vehicles[i]["timePlaced"]+stepThroughTime
                                vehicles[i]["currentPos"]+=1

                                #update LEDsStateNew
                                pos=vehicles[i]["currentPos"]
                                leadingPos=pos+vehicles[i]["visionRange"]
                                trailingPos=pos-vehicles[i]["visionRange"]

                                if trailingPos>=LEDsNum:
                                        #removeVehicle
                                        for x in range(i,len(vehicles)):
                                                vehicles[x]=vehicles[x+1]
                                
                                if(leadingPos<LEDsNum):#trailing LED to leading LED must be changed to high
                                        for i in range(trailingPos,leadingPos+1):
                                                LEDsStateNew[i]=1

                                trailingPos=trailingPos-1#two less characters
                                if(trailingPos>=0 and trailingPos<LEDsNum):#one LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                                        if LEDsStateNew[trailingPos]=="-":
                                                LEDsStateNew[trailingPos]=0
                                        elif LEDsStateNew[trailingPos]==1:
                                                LEDsStateNew[trailingPos]=1
                                        else:
                                                LEDsStateNew[trailingPos]=0
                                                
                        else:
                                #passToLeadingPi[0]=vehicles[i]
                                vehicles.pop(i)
                                #a=1#included because the else statment must have a body
                                #Pass vehicle to next pi

def addVehicleStartingLEDs(sensorPassed):
        for i in range((sensorPassed-1)*LEDsMult+1,(sensorPassed+1)*LEDsMult):
                if i>=0 and i<LEDsNum:
                        LEDsState[i]=1
                        
def removeVehicleStartingLEDs(sensorPassedBefore):
        for i in range((sensorPassedBefore-1)*LEDsMult+1,(sensorPassedBefore+1)*LEDsMult):
                if i>=0 and i<LEDsNum:
                        LEDsStateNew[i]=0

def updateStateFromNew():
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

def retrieveFirstVehicleSpeed(): #Return -1 if vehicle array in previous sensor is empty, if vehicle array has values, pop last value(get elements time and remove element )
        return -1
              

def calcSpeed(distance, time):
    return distance/time 
              
def isNewVehicle(sensorPassed):
    if expectedSensorPass[sensorPassed]==-1:
        return 1
    else: 
        return 0
              
def updateExpectedSensorPass(sensor, vehicle):
    if sensor<sensorsNum:
        expectedSensorPass[sensor]=vehicle
        expectedSensorPass[sensor-1]=-1
    else:
            passToLeadingPi[1]=vehicle
            expectedSensorPass[sensor]=-1
        #a=1 #include because else must have a body
        #For the next pi, call this same function pass the same vehicle but pass  the sensor 0 instead

def readFromFile():
        if os.path.isfile('./receiveFromTrailingPi.p'):
                return pickle.load(open("receiveFromTrailingPi.p","rb"))
        else:
                receiveFromTrailingPiTemp=[-1]
                pickle.dump(receiveFromTrailingPiTemp,open("receiveFromTrailingPi.p","wb"))
                return pickle.load(open("receiveFromTrailingPi.p","rb"))

        

def writeToFile(passToLeadingPi):
        pickle.dump(passToLeadingPi,open("passToLeadingPi.p","wb"))

def updateStateLEDFromRetrieved():
        
              
def main():
    try:
            resetLights()
            run =True
            firstVehicleSpeed=0
            passToLeadingPi=[-1]*3
            receiveFromTrailingPi=[]
            

            
            setAllSensorsDistance(5)
            setAllLEDsDistance()

            #used for setting up which light and sensor goes to which physical location
            #testLight()
            #testSensor()

            initSensorState()
            initLEDsState()
            initLEDsStateNew()
            
            while run:
                    initLEDsStateNew() #ensures the stateNew is empty
                    
                    receiveFromTrailingPi=readFromFile()
                    writeToFile(passToLeadingPi)
                    
                    print(receiveFromTrailingPi)
                    print(passToLeadingPi)
                    time.sleep(5)
                    
                    #Keeps scanning for motion
                    for i in range(0,sensorsNum):
                            state = scan(Sensors[i])

                            if state and sensorState[i]==0:
                                    
                                    sensorTime[i]=time.clock()#the time which the sensor was triggered is stored

                                    print(state)

                                    sensorState[i]=1
                                    
                                    #create new vehicle if a sensor is passed and previous sensor has no vehicles to traverse
                                    if isNewVehicle(i):
                                            #addVehicle
                                            vehicles.append(vehicle(i*LEDsMult,sensorTime[i],-1,-1))
                                            addVehicleStartingLEDs(i)
                                            
                                            updateExpectedSensorPass(i+1, len(vehicles)-1)
                                    else:
                                            #Since vehicle already exist, update its speed with the new speed
                                            
                                            #If speed=-1, then the starting lights must be removed
                                            if vehicles[expectedSensorPass[i]]["speed"]==-1:
                                                removeVehicleStartingLEDs(i-1)
                                            
                                            if i-1<0:
                                                vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-sensorTime[i-1])
                                            else:
                                                #for now treat it as though there is no previous pi, this line will be removed
                                                vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-0)

                                                #retrieve last sensors speed if it isnt -1
                                                #if(receiveFromTrailingPi[0]!=-1)
                                                #        vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-receiveFromTrailingPi[0])
                                                #Retrieve last sensorTime from the previous pi
                                                
                                            #Update vision range because speed changed
                                            vehicles[expectedSensorPass[i]]["visionRange"]= calcVisionRange(vehicles[expectedSensorPass[i]]["speed"])


                            elif state and sensorState[i]==1:
                                    sensorState[i]=1
                            elif state==0 and sensorState[i]==1:
                                    sensorState[i]=0

                    #turn on lights
                    stepThrough()
                    updateStateFromNew()
                    turnOnLEDs()



                        
                    
    except KeyboardInterrupt:
            run = False
    finally:
        GPIO.cleanup();

if __name__ == "__main__": 
    main()
