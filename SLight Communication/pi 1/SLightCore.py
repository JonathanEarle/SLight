#!/usr/bin/env python3

#add pi to pi communication to lines: ??(pass lights ahead to light) 167(pass vehicle to leading pi), 222(pass expectedSensorTime), 271(Retrieve last sensorTime from the previous pi)

import os
import pickle
import time
import threading
# import serverEnd
# import serverStart
# import clientEnd
# import clientStart

#import RPi.GPIO as GPIO
from EmulatorGUI import GPIO
GPIO.setmode(GPIO.BCM)

vehicles = []

#LEDS = [16,12,17,27,5,20]#GPIO of LED
#Sensors = [23,18,24]#GPIO of sensor
#Sensors = [23,18]


#testing LEDs and sensorsDistance
LEDS = [15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3]#20 LEDS
Sensors = [14,25,20,6,22]#5snesors

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
lastPiSensorTime=-1

start="serv1"
end="serv2"

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
    if curr !=0:
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
                        
#                        if state:
#                            print(i)
                        
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

def updateLEDsStateNew(pos,update):
    if update==1:
        LEDsStateNew[pos]=1
    else:
        if LEDsStateNew[pos]=="-":
            LEDsStateNew[pos]=0
        elif LEDsStateNew[pos]==1:
            LEDsStateNew[pos]=1
        else:
            LEDsStateNew[pos]=0
        
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
                                
                                #updateExpectedSensorPass(i+1, len(vehicles)-1)
                                #if vehicles[i]["currentPos"] % LEDsMult==0:
                                    #updateExpectedSensorPass(int(vehicles[i]["currentPos"] / LEDsMult)+1, i)

                                #update LEDsStateNew
                                pos=vehicles[i]["currentPos"]
                                leadingPos=pos+vehicles[i]["visionRange"]
                                trailingPos=pos-vehicles[i]["visionRange"]

                                if trailingPos>=LEDsNum:
                                        #passToLeadingPi-newVehicle
                                        passToLeadingPi.newVehicle(vehicles[x])
                                        
                                        #removeVehicle
                                        for x in range(i,len(vehicles)):
                                                vehicles[x]=vehicles[x+1]
                                
                                #trailing LED to leading LED must be changed to high
                                tempTrailing=[]#init to an array then proceed to append
                                tempLeading=[]#init to an array then proceed to append
                                for i in range(trailingPos,leadingPos+1):
                                        if i<0: #PassToTrailingPi-light
                                            tempTrailing.append(LEDsNum-i)
                                        elif i>=LEDsNum:#PassToLeadingPi-light
                                            tempLeading.append(i-LEDsNum)
                                        else:
                                            updateLEDsStateNew(i,1)
                                        
                                PassToTrailingPi.light(tempTrailing)
                                PassToLeadingPi.light(tempLeading)

                                trailingPos=trailingPos-1#two less characters
                                
                                #one LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                                if(trailingPos>=0):
                                        updateLEDsStateNew(trailingPos,0)
                                else:
                                        #PassToTrailingPi-fade
                                        tempTrailing=[]
                                        tempTrailing.append(trailingPos)
                                        PassToTrailingPi.fade(tempTrailing)
                                                
                    else:
                            tempVehicle=vehicles.pop(i)
                            tempVehicle["currentPos"]=0 #New vehicle entering the beginning of the track will be at currentPos=0
                            PassToLeadingPi.newVehicle(tempVehicle)
                            #Pass vehicle to next pi

def addVehicleStartingLEDs(sensorPassed):
        global PassToLeadingPi
        global PassToTrailingPi
        tempLeading=[]
        tempTrailing=[]
        for i in range((sensorPassed-1)*LEDsMult+1,(sensorPassed+1)*LEDsMult):
                if i>=0 and i<LEDsNum:
                        LEDsState[i]=1
                elif i<0:
                        #PassToTrailingPi-Light
                        tempTrailing.append(i)
                elif i>=LEDsNum:
                        #PassToLeadingPi-Light
                        tempLeading.append(i)
                        
        PassToLeadingPi.light(tempLeading)
        PassToTrailingPi.light(tempTrailing)
        PassToTrailingPi.printThis()
                   
                        
def removeVehicleStartingLEDs(sensorPassedBefore):
        tempLeading=[]
        tempTrailing=[]
        for i in range((sensorPassedBefore-1)*LEDsMult+1,(sensorPassedBefore+1)*LEDsMult):
                if i>=0 and i<LEDsNum:
                        updateLEDsStateNew(i,0)
                elif i<0:
                        #PassToTrailingPi-Light
                        tempTrailing.append(i)
                elif i>=LEDsNum:
                        #PassToLeadingPi-Light
                        tempLeading.append(i)
                        
        PassToLeadingPi.fade(tempLeading)
        PassToTrailingPi.fade(tempTrailing)
         

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
        #PassToLeadingPi-expectedSensorUpdate
        PassToLeadingPi.expectedSensorUpdate(vehicle)
        expectedSensorPass[sensor]=-1


#def updateStateLEDFromRetrieved():
       
    

class passToLeadingPi:
    
    def __init__(self):
        self.data={"light":None,"fade":None,"newVehicle":None,"expectedSensorUpdate":None,"lastSensorTime":None}
        self.change=0
    
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para):
        self.data["fade"]=para
        self.change=1
        
    def newVehicle(self,para):
        self.data["newVehicle"]=para
        self.change=1
        
    def expectedSensorUpdate(self,para):
        self.data["expectedSensorUpdate"]=para
        self.change=1
        
    def lastSensorTime(self,para):
        self.data["lastSensorTime"]=para
        self.change=1
        
    def setData(self,data):
        self.data=data
        self.change=1
        
    def getData(self):
        return self.data
        
    def printThis(self):
        print(self.data)
    
    def send(self):
        #if self.change==1:
            #send data to leading pi
            fromEndToStart()
            #reinitialize data
            self.data={"light":None,"fade":None,"newVehicle":None,"expectedSensorUpdate":None,"lastSensorTime":None}
            self.change=0
            
    
class receiveFromTrailingPi:
    
    def __init__(self):
        self.data={"light":None,"fade":None,"newVehicle":None,"expectedSensorUpdate":None,"lastSensorTime":None}
        self.change=0
    
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para):
        if self.data["fade"]==None:
            self.data["fade"]=para
        else:
            for i in range(0,len(para)):
                try:
                    index=self.data["fade"].index(para[i])
                    self.data["fade"].insert(index,para[i])
                except:
                    self.data["fade"].append(para[i])
                    
        self.change=1
        
    def newVehicle(self,para):
        self.data["newVehicle"]=para
        self.change=1
        
    def expectedSensorUpdate(self,para):
        self.data["expectedSensorUpdate"]=para
        self.change=1
        
    def lastSensorTime(self,para):
        self.data["lastSensorTime"]=para
        self.change=1
        
    def setData(self,data):
        self.data=data
        self.change=1
        
    def getData(self):
        return self.data
        
    def printThis(self):
        print(self.data)

    def isChanged(self):
        if self.change==1:
            return 1
        else:
            return 0
            
class passToTrailingPi:
    def __init__(self):
        self.data={"light":None,"fade":None}
        self.change=0
        
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para):
        self.data["fade"]=para
        self.change=1
    
    def setData(self,data):
        self.data=data
        self.change=1
        
    def getData(self):
        return self.data
        
    def printThis(self):
        print(self.data)
    
    def send(self):
        #if self.change==1:
            #send data to trailing pi
            fromStartToEnd()
            #reinitialize data
            self.data={"light":None,"fade":None}
            self.change=0
    
class receiveFromLeadingPi:
    def __init__(self):
        self.data={"light":None,"fade":None}
        self.change=0
        
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para):
        if self.data["fade"]==None:
            self.data["fade"]=para
        else:
            for i in range(0,len(para)):
                    self.data["fade"].append(para[i])
                    
        self.change=1
        
    def setData(self,data):
        self.data=data
        self.change=1
        
    def getData(self):
        return self.data
        
    def printThis(self):
        print(self.data)
        
    def isChanged(self):
        if self.change==1:
            return 1
        else:
            return 0
    

PassToLeadingPi=passToLeadingPi()
ReceiveFromTrailingPi=receiveFromTrailingPi()
PassToTrailingPi=passToTrailingPi()
ReceiveFromLeadingPi=receiveFromLeadingPi()
     

def fromStartToEnd():
    ReceiveFromLeadingPi.setData(PassToTrailingPi.getData())

def fromEndToStart():
    ReceiveFromTrailingPi.setData(PassToLeadingPi.getData())
     
def updateExpectedSensorFromPi():
    if ReceiveFromTrailingPi.getData()["expectedSensorUpdate"]!= None:
        expectedSensorPass[0]=ReceiveFromTrailingPi.getData()["expectedSensorUpdate"]
    


    
def main():
    try:
            resetLights()
            run =True
            firstVehicleSpeed=0
            
            setAllSensorsDistance(5)
            setAllLEDsDistance()
                
            global ReceiveFromTrailingPi
            global ReceiveFromLeadingPi
            global PassToLeadingPi
            global PassToTrailingPi
            global lastPiSensorTime
            
            #used for setting up which light and sensor goes to which physical location
            #testLight()
            #testSensor()

            initSensorState()
            initLEDsState()
            initLEDsStateNew()
            
            while run:
                    initLEDsStateNew() #ensures the stateNew is empty

                    #receive from leading pi
                    #if ReceiveFromLeadingPi.isChanged()==1:
                    #receive all pi data
                    #receive light
                    lights=ReceiveFromLeadingPi.getData()["light"]
                    if lights!=None:
                        for i in range(0,len(lights)):
                            updateLEDsStateNew(lights[i],1)
                    #receive fade
                    fades=ReceiveFromLeadingPi.getData()["fade"]
                    if fades!=None:
                        for i in range(0,len(fades)):
                            updateLEDsStateNew(fades[i],0)
                        
                    #after receiving all data reset data contained for next iteration
                    ReceiveFromLeadingPi=receiveFromLeadingPi() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist
                    
                    #receive from trailing pi
                    #if ReceiveFromTrailingPi.isChanged()==1:
                    #receive all pi data
                    updateExpectedSensorFromPi()#receive expectedSensorTime
                    #receive light
                    lights=ReceiveFromTrailingPi.getData()["light"]
                    if lights!=None:
                        for i in range(0,len(lights)):
                            updateLEDsStateNew(lights[i],1)
                    #receive fade
                    fades=ReceiveFromTrailingPi.getData()["fade"]
                    if fades!=None:
                        for i in range(0,len(fades)):
                            updateLEDsStateNew(fades[i],0)
                    #receive newVehicle
                    if ReceiveFromTrailingPi.getData()["newVehicle"]!=None:
                        vehicles.append(ReceiveFromTrailingPi.getData()["newVehicle"])
                        #addVehicleStartingLEDs(0)#will always be pos 0 since it now exited the previous pis track
                        updateExpectedSensorPass(1, len(vehicles)-1)
                    #receive lastSensorTime
                    if ReceiveFromTrailingPi.getData()["lastSensorTime"]!=None:
                        lastPiSensorTime=ReceiveFromTrailingPi.getData()["lastSensorTime"]

                    #after receiving all data reset data contained for next iteration
                    ReceiveFromTrailingPi=receiveFromTrailingPi() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist
                    
                    #Keeps scanning for motion
                    for i in range(0,sensorsNum):
                            state = scan(Sensors[i])

                            if state and sensorState[i]==0:
                                    
                                    sensorTime[i]=time.clock()#the time which the sensor was triggered is stored

                                    #PassToLeadingPi-LastSensorTime
                                    if state==sensorsNum-1:
                                        PassToLeadingPi.lastSensorTime(sensorTime[i])

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
                                                #vehicles[expectedSensorPass[i]]["currentPos"]=20
                                                #print(vehicles[expectedSensorPass[i]]["currentPos"])
                                            
                                            if i-1<0:#if this condition is met, then the sensorTime of the previous pi will be required to complete the speed update
                                                vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-sensorTime[i-1])
                                            else:
                                                #for now treat it as though there is no previous pi, this line will be removed
                                                vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-lastPiSensorTime)

                                                
                                            #Update vision range because speed changed
                                            vehicles[expectedSensorPass[i]]["visionRange"]= calcVisionRange(vehicles[expectedSensorPass[i]]["speed"])


                            elif state and sensorState[i]==1:
                                    sensorState[i]=1
                            elif state==0 and sensorState[i]==1:
                                    sensorState[i]=0
                    
                    #pass and receive data
                    
                    #creates cycle
                    PassToLeadingPi.send()
                    PassToTrailingPi.send()
                    
                    #pi to pi communication
                    # ReceiveFromLeadingPi.setData(clientEnd.rec())
                    # ReceiveFromTrailingPi.setData(clientStart.rec())
                    # serverEnd.send(PassToLeadingPi.getData)
                    # serverStart.send(PassToTrailingPi.getData)
                    
                    
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
