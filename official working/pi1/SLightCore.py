from firebase import firebase
import datetime
import ast
import os
import pickle
import time
import threading
import serverEnd
import serverStart
import clientEnd
import clientStart
import datetime
import time
import calendar

import RPi.GPIO as GPIO
#from EmulatorGUI import GPIO
GPIO.setmode(GPIO.BCM)
Firebase =firebase.FirebaseApplication('https://prog-c99a8.firebaseio.com/')
#Firebase =firebase.FirebaseApplication('https://slight-91c01.firebaseio.com/')

def pushData(dataModel):
    ts = time.time()
    hour = datetime.datetime.fromtimestamp(ts).strftime("%H")
    minute = datetime.datetime.fromtimestamp(ts).strftime("%M")
    day = datetime.datetime.fromtimestamp(ts).strftime("%d")
    year= datetime.datetime.fromtimestamp(ts).strftime("%Y")
    month= datetime.datetime.fromtimestamp(ts).strftime("%m")
    parent = "Pi_"+str(dataModel["id"])+"/" +year+"/" + calendar.month_name[int(month)] + "/" +day +"/" 
    Firebase.put(parent+"/"+hour +"/"+ str(minute) ,"No Of Cars",dataModel["numOfNewCars"])
    Firebase.put(parent+"/"+hour +"/"+ str(minute),"Speed",dataModel["avgSpeed"]);
    Firebase.put(parent+"/"+hour +"/"+ str(minute),"LEDsTimeOn",dataModel["LEDsTurnedOn"]);
    # saves average each hour


# Sets the GPIO Pins of the PI's sensors to send input to PI 
def setGPIOIn(sensors):
    for i in range(0,len(sensors)):
        GPIO.setup(sensors[i],GPIO.IN)

# Sets the GPIO Pins of the PI's LEDs to receive output from the PI 
def setGPIOOut(LEDS):
    for i in range(0,len(LEDS)):
        GPIO.setup(LEDS[i],GPIO.OUT)

# Sets the distance between all sensors to be of even distance which is received as an argument
def setAllsensorsDistance(sensors,sensorsDistance,distance):
    for i in range(0,len(sensors)):
        sensorsDistance.append(distance)
        
# Based on the amount of LEDs that are controlled by the PI, the LEDs distance is calculated evenly based on the sensors distance(most likely set by the function above)
def setAllLEDsDistance(sensors,sensorsDistance,LEDsMult,LEDsDistance):
    for i in range(0,len(sensors)):
        if i==0:
            dist=sensorsDistance[i]
            avg=dist/LEDsMult
        else:
            dist=sensorsDistance[i]
            avg=dist/LEDsMult
        
        for j in range(i*LEDsMult,((i+1)*LEDsMult)):
            LEDsDistance.append(avg)
        
# Turns on associated Light by the index number passed 
def lighton(LEDS,i):
        GPIO.output(LEDS[i],GPIO.HIGH)

# Turns off associated Light by the index number passed
def lightoff(LEDS,i):
        GPIO.output(LEDS[i],GPIO.LOW)

# Function used to detect if an object has passed the sensor or not
def scan(S): 
    curr= GPIO.input(S)
    # if curr !=0: # For python 3.5
    if curr ==0: # For python 2.7
        return S    
    else:     
        return 0
                
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
                
# Used to instantiate vehicle with values since a dictionary(dict) type was used to store a vehicles associated data
def vehicle(CurrentPos,TimePlaced,Speed,VisionRange):
        temp={"currentPos": CurrentPos, "timePlaced": TimePlaced, "speed": Speed, "visionRange": VisionRange, "maxSpeed":0, "sensorsPassed":0 , "avgSpeed": 0}
        return temp

#*(to rename) Calculation of speed, Application of the formula: Speed = Distance/Time
def calcStepThroughTime(LEDsDistance,speed,currentPos):
        return LEDsDistance[currentPos]/speed

#*(to implement calculation) Vision range is calculated based on how fast the vehicle is travelling, this is necessary because a faster vehicle will need to vision ahead and behind his/her vehicle to then react to a situation
def calcVisionRange(timeDifference):
        return 1

# Updates LEDsStateNew to state passed
def updateLEDsStateNew(LEDsStateNew,pos,update):
    if update==1:
        LEDsStateNew[pos]=1
    else:
        if LEDsStateNew[pos]=="-":
            LEDsStateNew[pos]=0
        elif LEDsStateNew[pos]==1:
            LEDsStateNew[pos]=1
        else:
            LEDsStateNew[pos]=0
        
# Turns on light ahead of vehicles expected positon and turns off lights that are no longer needed since the vehicle has passed
def stepThrough(LEDsStateNew,LEDsDistance,LEDsNum,vehicles,passToTrailingPi,passToLeadingPi,dataModel):
    currentTime=time.clock()
    lengthArr = len(vehicles)
    i=0
    while i<lengthArr: # Light and fade LEDs for all vehicles that entered the tract
        if vehicles[i]["speed"]!=-1: # If the vehicle has a speed of 0 then it has not only just entered the track(as well as all linked tracks), therefore a speed cannot be calculated to determine what lights to turn on. (not controlled here but all LEDs between the sensor passed, the next sensor and previous sensor is turned on) 
            if vehicles[i]["currentPos"]<LEDsNum: # If vehicle is still being controlled by this PI, if not the vehicles data is passed to the leading PI
                stepThroughTime=calcStepThroughTime(LEDsDistance,vehicles[i]["speed"],vehicles[i]["currentPos"]) # Speed Calcualted
            
                if stepThroughTime+vehicles[i]["timePlaced"] <currentTime: # If the vehicles speed and the time it was placed determines if at the current time the LEDs should right shift 1 place down
                    # Change timeplaced and currentPosition
                    vehicles[i]["timePlaced"]=vehicles[i]["timePlaced"]+stepThroughTime
                    vehicles[i]["currentPos"]+=1

                    # Update LEDsStateNew
                    pos=vehicles[i]["currentPos"]
                    leadingPos=pos+vehicles[i]["visionRange"]
                    trailingPos=pos-vehicles[i]["visionRange"]
                    
                    # Trailing LED to leading LED must be changed to high
                    tempTrailing=[]# init to an array then proceed to append
                    tempLeading=[]# init to an array then proceed to append
                    for i in range(trailingPos,leadingPos+1):
                        if i<0: # passToTrailingPi-light
                            tempTrailing.append(LEDsNum-i)
                        elif i>=LEDsNum:# passToLeadingPi-light
                            tempLeading.append(i-LEDsNum)
                        else:
                            updateLEDsStateNew(LEDsStateNew,i,1)
                            
                    # Pass data of which LEDs to turn on
                    passToTrailingPi.light(tempTrailing)
                    passToLeadingPi.light(tempLeading)

                    trailingPos=trailingPos-1#* Two less characters
                    
                    # One LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                    if trailingPos>=0:
                        updateLEDsStateNew(LEDsStateNew,trailingPos,0)
                    else:
                        #P assToTrailingPi-fade
                        tempTrailing=[]
                        tempTrailing.append(LEDsNum-(trailingPos*-1))
                        passToTrailingPi.fade(tempTrailing)
                                        
            else:   
                #Pass vehicle to next pi
                tempVehicle=vehicles.pop(i) # Remove vehicle from this PIs list
                tempVehicle["currentPos"]=0 # New vehicle entering the beginning of the track will be at currentPos=0
                passToLeadingPi.newVehicle(tempVehicle)
                lengthArr = len(vehicles)
                
                
        i=i+1;
                    
#*(vision range should also be accounted for in the range) If the vehicle has now entered the track then the speed cannot be calculated unless there are two points, therefore all LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
def addVehicleStartingLEDs(passToLeadingPi,passToTrailingPi,LEDsMult,LEDsNum,LEDsState,sensorPassed):
    tempLeading=[]
    tempTrailing=[]
    for i in range(0,(sensorPassed+1)*LEDsMult): # All LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
        if i>=0 and i<LEDsNum:
                LEDsState[i]=1
        elif i>=LEDsNum:
                #passToLeadingPi-Light
                tempLeading.append(i)
                    
    passToLeadingPi.light(tempLeading)
    passToTrailingPi.light(tempTrailing)
                   
# Vehicle speed can now be calculated therefore the LEDs that was turned on for vision in the previous function is turned off
def removeVehicleStartingLEDs(LEDsStateNew,passToLeadingPi,passToTrailingPi,LEDsMult,LEDsNum,sensorPassedBefore):
    tempLeading=[]
    tempTrailing=[]
    for i in range(0,(sensorPassedBefore+1)*LEDsMult):
        if i>=0 and i<LEDsNum:
            updateLEDsStateNew(LEDsStateNew,i,0)
        elif i>=LEDsNum:
            #passToLeadingPi-Fade
            tempLeading.append(i)
                    
    passToLeadingPi.fade(tempLeading)
    passToTrailingPi.fade(tempTrailing)
         
# LEDsState value is correctly assigned from the buffer LEDsStateNew, whose purpose was to ensure different vehicles LEDs light and fade did not clash due to sequence of operations
def updateStateFromNew(LEDsState,LEDsStateNew,LEDsNum):
    for i in range(0,LEDsNum):
        if LEDsStateNew[i]!="-":
            LEDsState[i]=LEDsStateNew[i]
                
# Turns on all LEDs that has a state of 1 and turns off all that has a state of 0
def turnOnLEDs(LEDsState,LEDsNum,LEDS):
    for i in range(0,LEDsNum):
        if LEDsState[i]:
            lighton(LEDS,i)
        else:
            lightoff(LEDS,i)

# Initialized the LEDs state to all be off
def initLEDsState(LEDsState,LEDsNum):
    for i in range(0,LEDsNum):
        LEDsState[i]=0

# Initialized the LEDsStateNew to all be off
def initLEDsStateNew(LEDsStateNew,LEDsNum):
    for i in range(0,LEDsNum):
        LEDsStateNew[i]="-"

# Initialized SensorState to all be off
def initSensorState(sensorState,sensorsNum):
    for i in range(0,sensorsNum):
        sensorState[i]=0
              
# Calcualtes Speed
def calcSpeed(distance, time):
    return distance/time 

# If it is a new vehicle that is entering the track
def isNewVehicle(expectedSensorPass,sensorPassed):
    if expectedSensorPass[sensorPassed]==-1:
        return 1
    else: 
        return 0
              
# Update ExpectedSensorPass at a position to the vehicle index passed
def updateExpectedSensorPass(expectedSensorPass,sensorsNum,passToLeadingPi,sensor,vehicle):
    if sensor<sensorsNum:
        expectedSensorPass[sensor]=vehicle
        expectedSensorPass[sensor-1]=-1
    else:
        #passToLeadingPi-expectedSensorUpdate
        passToLeadingPi.expectedSensorUpdate(vehicle)
        expectedSensorPass[sensor]=-1

def PassToLeadingPiSend(passToLeadingPi,receiveFromTrailingPi):
    fromEndToStart(receiveFromTrailingPi,passToLeadingPi)
    return PassToLeadingPi()
    
def PassToTrailingPiSend(receiveFromLeadingPi,passToTrailingPi):
    fromStartToEnd(receiveFromLeadingPi,passToTrailingPi)
    return PassToTrailingPi()
    
        
class PassToLeadingPi:
    
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
    
    def isChanged(self):
        if self.change==1:
            return 1
        else:
            return 0
    
    def send(self):
        #if self.change==1:
            #send data to leading pi
            #*fromEndToStart(receiveFromTrailingPi,passToLeadingPi)
            #reinitialize data
            self.data={"light":None,"fade":None,"newVehicle":None,"expectedSensorUpdate":None,"lastSensorTime":None}
            self.change=0
            
# Encapsulation of data 
class ReceiveFromTrailingPi:
    
    def __init__(self):
        self.data={"light":None,"fade":None,"newVehicle":None,"expectedSensorUpdate":None,"lastSensorTime":None}
        self.change=0
    
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para): #instead of overwriting the data, consider the case where data already exists and append to it. This is necessary because of the case of startign LEDs being removed
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

# Encapsulation of data 
class PassToTrailingPi:
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
    
    def isChanged(self):
        if self.change==1:
            return 1
        else:
            return 0
    
    def send(self):
        #if self.change==1:
            #send data to trailing pi
            #*fromStartToEnd(receiveFromLeadingPi,passToTrailingPi)
            #reinitialize data
            self.data={"light":None,"fade":None}
            self.change=0
    
# Encapsulation of data 
class ReceiveFromLeadingPi:
    def __init__(self):
        self.data={"light":None,"fade":None}
        self.change=0
        
    def light(self,para):
        self.data["light"]=para
        self.change=1
        
    def fade(self,para): #instead of overwriting the data, consider the case where data already exists and append to it. This is necessary because of the case of startign LEDs being removed
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
    
#*(to remove) For testing purposes this is used to create a cycle of the track in only one PI, simulates data transfer
def fromStartToEnd(receiveFromLeadingPi,passToTrailingPi):
    receiveFromLeadingPi.setData(passToTrailingPi.getData())

#*(to remove) For testing purposes this is used to create a cycle of the track in only one PI, simulates data transfer
def fromEndToStart(receiveFromTrailingPi,passToLeadingPi):
    receiveFromTrailingPi.setData(passToLeadingPi.getData())
     
# If expectedSensorUpdate is needed by the PI and it is passed, store it
def updateExpectedSensorFromPi(expectedSensorPass,receiveFromTrailingPi):
    if receiveFromTrailingPi.getData()["expectedSensorUpdate"]!= None:
        expectedSensorPass[0]=receiveFromTrailingPi.getData()["expectedSensorUpdate"]

# Receive from leading pi
def ReceiveFromLeadingPiStore(receiveFromLeadingPi,LEDsStateNew):
    # Receive light
    lights=receiveFromLeadingPi.getData()["light"]
    if lights!=None:
        for i in range(0,len(lights)):
            updateLEDsStateNew(LEDsStateNew,lights[i],1)
    # Receive fade
    fades=receiveFromLeadingPi.getData()["fade"]
    if fades!=None:
        for i in range(0,len(fades)):
            updateLEDsStateNew(LEDsStateNew,fades[i],0)
        
    # After receiving all data reset data contained for next iteration
    return ReceiveFromLeadingPi() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist
        
# Receive from trailing pi
def ReceiveFromTrailingPiStore(receiveFromTrailingPi,LEDsStateNew,expectedSensorPass,vehicles,lastPiSensorTime,sensorsNum,passToLeadingPi):
    updateExpectedSensorFromPi(expectedSensorPass,receiveFromTrailingPi)#receive expectedSensorTime
    #receive light
    lights=receiveFromTrailingPi.getData()["light"]
    if lights!=None:
        for i in range(0,len(lights)):
            updateLEDsStateNew(LEDsStateNew,lights[i],1)
    #receive fade
    fades=receiveFromTrailingPi.getData()["fade"]
    if fades!=None:
        for i in range(0,len(fades)):
            updateLEDsStateNew(LEDsStateNew,fades[i],0)
    #receive newVehicle
    if receiveFromTrailingPi.getData()["newVehicle"]!=None:
        veh=receiveFromTrailingPi.getData()["newVehicle"]
        veh["timePlaced"]=time.clock()
        vehicles.append(veh)
        #addVehicleStartingLEDs(0)#will always be pos 0 since it now exited the previous pis track
        updateExpectedSensorPass(expectedSensorPass,sensorsNum,passToLeadingPi,1, len(vehicles)-1)
    #receive lastSensorTime
    if receiveFromTrailingPi.getData()["lastSensorTime"]!=None:
        lastPiSensorTime=receiveFromTrailingPi.getData()["lastSensorTime"]

    #after receiving all data reset data contained for next iteration
    return ReceiveFromTrailingPi() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist

def pushDataModel(dataModel):
    Firebase =firebase.FirebaseApplication('https://slight-91c01.firebaseio.com/')
    now = datetime.datetime.now()
    result = Firebase.put(str(now.year) + "/" + str(now.month) + "/" + str(now.day)  + "/" + str(now.hour), str(now.minute),dataModel)
    
def genLEDsFirebaseModel(LEDsNum):
    model= {}
    for i in range(0,LEDsNum):
        model[str(i)]=0
    return model
    
def updateLEDsModel(LEDsModel,timeDiff,LEDsState):
    for i in range(0,len(LEDsState)):
        if(LEDsState[i]):
            LEDsModel[str(i)]=LEDsModel[str(i)]+timeDiff
    return LEDsModel
    
def main():
    try:
        #Variables
        
        # Hard Coded LEDs and sensors as it relates to the PI's GPIO Pins
        #LEDS = [15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3]
        #sensors = [14,25,20,6,22]
        LEDS = [16,12,17,27,5,20,19,21]
        sensors = [23,18]
        vehicles = [] # An array that contains vehicles that are currently traversing the PI's track. The data each element contain is a dict in the format of: {"currentPos": CurrentPos, "timePlaced": TimePlaced, "speed": Speed, "visionRange": VisionRange}

        LEDsMult=int(len(LEDS)/len(sensors)) # How many LEDs that is between two sensors
        sensorsNum=len(sensors) # How many sensors that were entered
        sensorTime=[0]*sensorsNum # Time at which the sensor was passed, initialized to 0 because that is the lowest possible time that can be achieved
        sensorState=[0]*sensorsNum # Since the sensor is 'enabled' for the length of time the vehicle passes near the sensor, this is used to keep check of the exact point where the state changes from 0 to 1 which dictates exactly when the car has passed sensor. 
        expectedSensorPass=[-1]*sensorsNum # Keeps note of which vehicle is expected to pass which sensor, this is necessary for speed updates to occur to the correct vehicle as it passes another sensor

        LEDsNum=len(LEDS) # How many LEDs that were entered
        LEDsStateNew=[0]*LEDsNum # used to keep check of what the new state is after the set of "stepThrough" functions are run,single element can be, 1 meaning light on, 0 meaning light off, or - meaning keep corresponding state of LEDsState. Ensures a vehicle's associated LEDs does not clash with another vehicle's LEDs
        LEDsState=[0]*LEDsNum # single element can be either 1 meaning light on or 0 meaning light off

        LEDsDistance=[] # Distance from one sensor to another sensor, this is for the situation where street lights were already placed but with uneven distances between them for any particular reason
        sensorsDistance=[] # similar reason ^^
        lastPiSensorTime=-1 # The time the last sensor in the track was passed, this is stored to pass to the leading PI to calculate vehicles speed
        run =True
        
        # data to nbe use for pushing into firebase
        id=1
        dataModelInit={'id':id, 'avgSpeed': 0,'numOfNewCars' :0,'LEDsTurnedOn': {} }
        dataModel=dataModelInit
        now = datetime.datetime.now()
        min=now.minute
        secChanged=0
        LEDsModel=genLEDsFirebaseModel(LEDsNum)
        timeBeforeLEDUpdate=time.clock()
            
        # Set GPIO pins
        setGPIOIn(sensors)
        setGPIOOut(LEDS)
        
        # Init distance
        setAllsensorsDistance(sensors,sensorsDistance,5) 
        setAllLEDsDistance(sensors,sensorsDistance,LEDsMult,LEDsDistance)
            
        # Initialize data to be sent and reveived between PIs to ensure no garbage data
        passToLeadingPi=PassToLeadingPi()
        receiveFromTrailingPi=ReceiveFromTrailingPi()
        passToTrailingPi=PassToTrailingPi()
        receiveFromLeadingPi=ReceiveFromLeadingPi()
        
        # Used for setting up which light and sensor goes to which physical location
        
        # Init States
        initSensorState(sensorState,sensorsNum)
        initLEDsState(LEDsState,LEDsNum)

        while run:
            initLEDsStateNew(LEDsStateNew,LEDsNum) # Ensures the stateNew is empty
            
            # Pi to Pi communication
            receiveFromLeadingPi=ReceiveFromLeadingPiStore(receiveFromLeadingPi,LEDsStateNew)
            receiveFromTrailingPi=ReceiveFromTrailingPiStore(receiveFromTrailingPi,LEDsStateNew,expectedSensorPass,vehicles,lastPiSensorTime,sensorsNum,passToLeadingPi)
            
            # Keeps scanning for motion
            for i in range(0,sensorsNum):
                state = scan(sensors[i])
                if state and sensorState[i]==0: # Vehicle has now passed the sensor
                    sensorTime[i]=time.clock()#the time which the sensor was triggered is stored

                    # passToLeadingPi-LastSensorTime
                    if state==sensorsNum-1:
                        passToLeadingPi.lastSensorTime(sensorTime[i])

                    sensorState[i]=1
                    
                    #*(to delete fnction isNewVehicle) Create new vehicle if 1st sensor is passed
                    if i==0:
                        # AddVehicle
                        vehicles.append(vehicle(0,sensorTime[i],-1,-1))
                        addVehicleStartingLEDs(passToLeadingPi,passToTrailingPi,LEDsMult,LEDsNum,LEDsState,i)
                        updateExpectedSensorPass(expectedSensorPass,sensorsNum,passToLeadingPi,i+1, len(vehicles)-1) # Update expectedSensorPass of the next index to this vehicle that was just appended. This is to ensure that the correct vehicle speed is updated
                        
                        #increment car counter to pass to firebase
                        dataModel["numOfNewCars"]=dataModel["numOfNewCars"]+1
                    else:
                        # Since vehicle already exist, update its speed with the new speed
                        if vehicles[len(vehicles)-1]["speed"]==-1: # If the last vehicle that entered the track speed=-1, then the starting lights must be removed
                            removeVehicleStartingLEDs(LEDsStateNew,passToLeadingPi,passToTrailingPi,LEDsMult,LEDsNum,i-1)
                            #print(passToTrailingPi.getData()["fade"])
                            
                        if i-1<0: # if this condition is met, then the sensorTime of the previous pi will be required to complete the speed update
                             vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-lastPiSensorTime)
                        else:
                            #*(for now treat it as though there is no previous pi, this line will be removed)
                            vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-sensorTime[i-1])

                        #Update vision range because speed changed
                        vehicles[expectedSensorPass[i]]["visionRange"]= calcVisionRange(vehicles[expectedSensorPass[i]]["speed"])
                        
                        #add onto maxSpeed with current speed value to calulate avg
                        vehicles[expectedSensorPass[i]]["maxSpeed"]=vehicles[expectedSensorPass[i]]["maxSpeed"]+vehicles[expectedSensorPass[i]]["speed"]
                        vehicles[expectedSensorPass[i]]["sensorsPassed"]=vehicles[expectedSensorPass[i]]["sensorsPassed"]+1

                elif state and sensorState[i]==1: # Vehicle is still passing the sensor
                    sensorState[i]=1
                elif state==0 and sensorState[i]==1: # Vehicle has finished passing the sensor
                    sensorState[i]=0
            #pass and receive data
            
            #creates cycle if multiple PIs does not exist
            #passToLeadingPi=PassToLeadingPiSend(passToLeadingPi,receiveFromTrailingPi)
            #passToTrailingPi=PassToTrailingPiSend(receiveFromLeadingPi,passToTrailingPi)
            
            # PI to PI communication
            receiveFromLeadingPi.setData(ast.literal_eval(clientStart.rec()))
            receiveFromTrailingPi.setData(ast.literal_eval(clientEnd.rec()))
            serverEnd.send(passToLeadingPi.getData())
            serverStart.send(passToTrailingPi.getData())
            #reset pi to transfer data
            passToLeadingPi=PassToLeadingPi()
            passToTrailingPi=PassToTrailingPi()
            
            #turn on lights
            #print(LEDsStateNew)
            stepThrough(LEDsStateNew,LEDsDistance,LEDsNum,vehicles,passToTrailingPi,passToLeadingPi,dataModel)
            updateStateFromNew(LEDsState,LEDsStateNew,LEDsNum)
            timeAtLEDUpdate=time.clock()
            LEDsModel=updateLEDsModel(LEDsModel,timeAtLEDUpdate-timeBeforeLEDUpdate,LEDsState)
            timeBeforeLEDUpdate=timeAtLEDUpdate
            turnOnLEDs(LEDsState,LEDsNum,LEDS)
            
            # Push data to firebase if the minute changes
            now = datetime.datetime.now()
            if now.minute>min:
                # resetdata
                secChanged=0
                sec=now.second
                
                #calculate avgspeed 
                noOfCars=0
                avgSpeed=0
                maxSpeed=0
                for i in range(0,len(vehicles)):
                    print(vehicles[i]["maxSpeed"])
                    print(vehicles[i]["sensorsPassed"])
                    vehicles[i]["avgSpeed"]=vehicles[i]["maxSpeed"] / (vehicles[i]["sensorsPassed"]+1)#* # avg speed of that vehicle
                    maxSpeed=maxSpeed+vehicles[i]["avgSpeed"] #add average speed of all vehicles
                avgSpeed=maxSpeed /dataModel["numOfNewCars"] #calculate avg speed of all new vehicles
                #reset vehicles data for next minute
                for i in range(0,len(vehicles)):
                    vehicles[i]["avgSpeed"]=0
                    vehicles[i]["maxSpeed"]=0
                    vehicles[i]["sensorsPassed"]=0
                
                #append avgspeed 
                dataModel["avgSpeed"]=avgSpeed
                dataModel["LEDsTurnedOn"]=LEDsModel
                #pushData(dataModel)
                t1 = threading.Thread(target=pushData, args=(dataModel,))
                t1.start()
                
                #print dataModel
                print(dataModel)
                
                #reset data
                dataModel=dataModelInit
                LEDsModel=genLEDsFirebaseModel(LEDsNum)
                dataModel["LEDsTurnedOn"]=LEDsModel
                    
    except KeyboardInterrupt:
            run = False
    finally:
        GPIO.cleanup();

if __name__ == "__main__": 
    main()
