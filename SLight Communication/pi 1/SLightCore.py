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

vehicles = [] # An array that contains vehicles that are currently traversing the PI's track. The data each element contain is a dict in the format of: {"currentPos": CurrentPos, "timePlaced": TimePlaced, "speed": Speed, "visionRange": VisionRange}

# Hard Coded LEDs and Sensors as it relates to the PI's GPIO Pins
LEDS = [15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3]
Sensors = [14,25,20,6,22]

LEDsMult=int(len(LEDS)/len(Sensors)) # How many LEDs that is between two sensors
sensorsNum=len(Sensors) # How many Sensors that were entered
sensorTime=[0]*sensorsNum # Time at which the sensor was passed, initialized to 0 because that is the lowest possible time that can be achieved
sensorState=[0]*sensorsNum # Since the sensor is 'enabled' for the length of time the vehicle passes near the sensor, this is used to keep check of the exact point where the state changes from 0 to 1 which dictates exactly when the car has passed sensor. 
expectedSensorPass=[-1]*sensorsNum # Keeps note of which vehicle is expected to pass which sensor, this is necessary for speed updates to occur to the correct vehicle as it passes another sensor

LEDsNum=len(LEDS) # How many LEDs that were entered
LEDsStateNew=[0]*LEDsNum # used to keep check of what the new state is after the set of "stepThrough" functions are run,single element can be, 1 meaning light on, 0 meaning light off, or - meaning keep corresponding state of LEDsState. Ensures a vehicle's associated LEDs does not clash with another vehicle's LEDs
LEDsState=[0]*LEDsNum # single element can be either 1 meaning light on or 0 meaning light off

LEDsDistance=[] # Distance from one sensor to another sensor, this is for the situation where street lights were already placed but with uneven distances between them for any particular reason
sensorsDistance=[] # similar reason ^^
lastPiSensorTime=-1 # The time the last sensor in the track was passed, this is stored to pass to the leading PI to calculate vehicles speed

# Sets the GPIO Pins of the PI's sensors to send input to PI 
for i in range(0,len(Sensors)):
        GPIO.setup(Sensors[i],GPIO.IN)

# Sets the GPIO Pins of the PI's LEDs to receive output from the PI 
for i in range(0,len(LEDS)):
        GPIO.setup(LEDS[i],GPIO.OUT)

# Sets the distance between all sensors to be of even distance which is received as an argument
def setAllSensorsDistance(distance):
    for i in range(0,len(Sensors)):
        sensorsDistance.append(distance)
        
# Based on the amount of LEDs that are controlled by the PI, the LEDs distance is calculated evenly based on the sensors distance(most likely set by the function above)
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
        
# Turns on associated Light by the index number passed 
def lighton(i):
        GPIO.output(LEDS[i],GPIO.HIGH)

# Turns off associated Light by the index number passed
def lightoff(i):
        GPIO.output(LEDS[i],GPIO.LOW)

# Function used to detect if an object has passed the sensor or not
def scan(S): 
    curr= GPIO.input(S)
    if curr !=0:
        return S    
    else:     
        return 0
                
# Requests input of a LED number in the terminal and lights it for two seconds for u to determine which LED is which, terminate function by inputting "-1", This is used for setting up on the track
def testLight():
    while True:
        LED= input("Enter LED #: ")
        if LED==-1: # Terminating Condition
            break
        if LED>=0 and LED <LEDsNum: 
            lighton(LED)
            t = threading.Timer(2,lightoff,[LED]) # A thread is created with a timer of 2 seconds to turn off that light that was turned on
            t.start()

# function continuously checks for an object passing any sensor, when an object has passed a sensor that particular sensor index is printed on the terminal, This is used for setting up on the track
def testSensor():
    while True:
        for i in range(0,sensorsNum):
                state = scan(Sensors[i]) # State of the sensor[i] passed
                
                if state and sensorState[i]==0: # Vehicle has begun passing the sensor
                    print(i)
                    sensorState[i]=1
                elif state and sensorState[i]==1: # vehicle is currently still passing the sensor
                    sensorState[i]=1
                elif state==0 and sensorState[i]==1: # vehicle has passed the sensor  fully, therefore reset sensorState[i] to 0
                    sensorState[i]=0
                
# Used to instantiate vehicle with values since a dictionary(dict) type was used to store a vehicles associated data
def vehicle(CurrentPos,TimePlaced,Speed,VisionRange):
        temp={"currentPos": CurrentPos, "timePlaced": TimePlaced, "speed": Speed, "visionRange": VisionRange}
        return temp

#*(to rename) Calculation of speed, Application of the formula: Speed = Distance/Time
def calcStepThroughTime(speed,currentPos):
        return LEDsDistance[currentPos]/speed

#*(to implement calculation) Vision range is calculated based on how fast the vehicle is travelling, this is necessary because a faster vehicle will need to vision ahead and behind his/her vehicle to then react to a situation
def calcVisionRange(timeDifference):
        return 1

# Updates LEDsStateNew to state passed
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
        
# Turns on light ahead of vehicles expected positon and turns off lights that are no longer needed since the vehicle has passed
def stepThrough():
    currentTime=time.clock()
    
    for i in range(0,len(vehicles)): # Light and fade LEDs for all vehicles that entered the tract
        if vehicles[i]["speed"]!=-1: # If the vehicle has a speed of 0 then it has not only just entered the track(as well as all linked tracks), therefore a speed cannot be calculated to determine what lights to turn on. (not controlled here but all LEDs between the sensor passed, the next sensor and previous sensor is turned on) 
            if vehicles[i]["currentPos"]<LEDsNum: # If vehicle is still being controlled by this PI, if not the vehicles data is passed to the leading PI
                stepThroughTime=calcStepThroughTime(vehicles[i]["speed"],vehicles[i]["currentPos"]) # Speed Calcualted
            
                if stepThroughTime+vehicles[i]["timePlaced"] <currentTime: # If the vehicles speed and the time it was placed determines if at the current time the LEDs should right shift 1 place down
                    # Change timeplaced and currentPosition
                    vehicles[i]["timePlaced"]=vehicles[i]["timePlaced"]+stepThroughTime
                    vehicles[i]["currentPos"]+=1

                    # Update LEDsStateNew
                    pos=vehicles[i]["currentPos"]
                    leadingPos=pos+vehicles[i]["visionRange"]
                    trailingPos=pos-vehicles[i]["visionRange"]
                    
                    #*(is this needed? else statement takes care of this) Pass vehicles data to leading PI in the track because its new position is not controlled by the current PI
                    if trailingPos>=LEDsNum:
                        # passToLeadingPi-newVehicle
                        passToLeadingPi.newVehicle(vehicles[x])
                        
                        # RemoveVehicle
                        for x in range(i,len(vehicles)):
                            vehicles[x]=vehicles[x+1]
                    
                    # Trailing LED to leading LED must be changed to high
                    tempTrailing=[]# init to an array then proceed to append
                    tempLeading=[]# init to an array then proceed to append
                    for i in range(trailingPos,leadingPos+1):
                        if i<0: # PassToTrailingPi-light
                            tempTrailing.append(LEDsNum-i)
                        elif i>=LEDsNum:# PassToLeadingPi-light
                            tempLeading.append(i-LEDsNum)
                        else:
                            updateLEDsStateNew(i,1)
                            
                    # Pass data of which LEDs to turn on
                    PassToTrailingPi.light(tempTrailing)
                    PassToLeadingPi.light(tempLeading)

                    trailingPos=trailingPos-1#* Two less characters
                    
                    # One LED before trailing LED can be changed to low if possible,to simulate the removal of LEDs as the vehicle passes
                    if trailingPos>=0:
                        updateLEDsStateNew(trailingPos,0)
                    else:
                        #P assToTrailingPi-fade
                        tempTrailing=[]
                        tempTrailing.append(trailingPos)
                        PassToTrailingPi.fade(tempTrailing)
                                        
            else:   
                #Pass vehicle to next pi
                tempVehicle=vehicles.pop(i) # Remove vehicle from this PIs list
                tempVehicle["currentPos"]=0 # New vehicle entering the beginning of the track will be at currentPos=0
                PassToLeadingPi.newVehicle(tempVehicle)
                    
#*(vision range should also be accounted for in the range) If the vehicle has now entered the track then the speed cannot be calculated unless there are two points, therefore all LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
def addVehicleStartingLEDs(sensorPassed):
    global PassToLeadingPi
    global PassToTrailingPi
    tempLeading=[]
    tempTrailing=[]
    for i in range((sensorPassed-1)*LEDsMult+1,(sensorPassed+1)*LEDsMult): # All LEDs between the succeeding sensor and the previous sensor is turned on to give the most vision possible
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
                   
# Vehicle speed can now be calculated therefore the LEDs that was turned on for vision in the previous function is turned off
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
         
# LEDsState value is correctly assigned from the buffer LEDsStateNew, whose purpose was to ensure different vehicles LEDs light and fade did not clash due to sequence of operations
def updateStateFromNew():
    for i in range(0,LEDsNum):
        if LEDsStateNew[i]!="-":
            LEDsState[i]=LEDsStateNew[i]
                
# Turns on all LEDs that has a state of 1 and turns off all that has a state of 0
def turnOnLEDs():
    for i in range(0,LEDsNum):
        if LEDsState[i]:
            lighton(i)
        else:
            lightoff(i)

# Initialized the LEDs state to all be off
def initLEDsState():
    for i in range(0,LEDsNum):
        LEDsState[i]=0

# Initialized the LEDsStateNew to all be off
def initLEDsStateNew():
    for i in range(0,LEDsNum):
        LEDsStateNew[i]="-"

# Initialized SensorState to all be off
def initSensorState():
    for i in range(0,sensorsNum):
        sensorState[i]=0
              
# Calcualtes Speed
def calcSpeed(distance, time):
    return distance/time 

# If it is a new vehicle that is entering the track
def isNewVehicle(sensorPassed):
    if expectedSensorPass[sensorPassed]==-1:
        return 1
    else: 
        return 0
              
# Update ExpectedSensorPass at a position to the vehicle index passed
def updateExpectedSensorPass(sensor, vehicle):
    if sensor<sensorsNum:
        expectedSensorPass[sensor]=vehicle
        expectedSensorPass[sensor-1]=-1
    else:
        #PassToLeadingPi-expectedSensorUpdate
        PassToLeadingPi.expectedSensorUpdate(vehicle)
        expectedSensorPass[sensor]=-1

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
            
# Encapsulation of data 
class receiveFromTrailingPi:
    
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
    
# Encapsulation of data 
class receiveFromLeadingPi:
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
    
# Initialize data to be sent and reveived between PIs to ensure no garbage data
PassToLeadingPi=passToLeadingPi()
ReceiveFromTrailingPi=receiveFromTrailingPi()
PassToTrailingPi=passToTrailingPi()
ReceiveFromLeadingPi=receiveFromLeadingPi()
     
#*(to remove) For testing purposes this is used to create a cycle of the track in only one PI, simulates data transfer
def fromStartToEnd():
    ReceiveFromLeadingPi.setData(PassToTrailingPi.getData())

#*(to remove) For testing purposes this is used to create a cycle of the track in only one PI, simulates data transfer
def fromEndToStart():
    ReceiveFromTrailingPi.setData(PassToLeadingPi.getData())
     
# If expectedSensorUpdate is needed by the PI and it is passed, store it
def updateExpectedSensorFromPi():
    if ReceiveFromTrailingPi.getData()["expectedSensorUpdate"]!= None:
        expectedSensorPass[0]=ReceiveFromTrailingPi.getData()["expectedSensorUpdate"]

# Receive from leading pi
def receiveFromLeadingPiStore():
    # Receive light
    lights=ReceiveFromLeadingPi.getData()["light"]
    if lights!=None:
        for i in range(0,len(lights)):
            updateLEDsStateNew(lights[i],1)
    # Receive fade
    fades=ReceiveFromLeadingPi.getData()["fade"]
    if fades!=None:
        for i in range(0,len(fades)):
            updateLEDsStateNew(fades[i],0)
        
    # After receiving all data reset data contained for next iteration
    ReceiveFromLeadingPi=receiveFromLeadingPi() #no need to check if the value is None here since should this data be needed, it will be guaranteed to exist
        
# Receive from trailing pi
def receiveFromTrailingPiStore():        
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
                    
def main():
    try:
        run =True
        
        # Init distance
        setAllSensorsDistance(5) 
        setAllLEDsDistance()
            
        global ReceiveFromTrailingPi
        global ReceiveFromLeadingPi
        global PassToLeadingPi
        global PassToTrailingPi
        global lastPiSensorTime
        
        # Used for setting up which light and sensor goes to which physical location
        # testLight()
        # testSensor()
        
        # Init States
        initSensorState()
        initLEDsState()
        
        while run:
            initLEDsStateNew() # Ensures the stateNew is empty

            # Receive from leading pi
            receiveFromLeadingPiStore()
            # Receive from trailing pi
            receiveFromTrailingPiStore()
            
            # Keeps scanning for motion
            for i in range(0,sensorsNum):
                state = scan(Sensors[i])
                if state and sensorState[i]==0: # Vehicle has now passed the sensor
                    sensorTime[i]=time.clock()#the time which the sensor was triggered is stored

                    # PassToLeadingPi-LastSensorTime
                    if state==sensorsNum-1:
                        PassToLeadingPi.lastSensorTime(sensorTime[i])

                    sensorState[i]=1
                    
                    # Create new vehicle if a sensor is passed and previous sensor has no vehicles to traverse
                    if isNewVehicle(i):
                        # AddVehicle
                        vehicles.append(vehicle(i*LEDsMult,sensorTime[i],-1,-1))
                        addVehicleStartingLEDs(i)
                        updateExpectedSensorPass(i+1, len(vehicles)-1) # Update expectedSensorPass of the next index to this vehicle that was just appended. This is to ensure that the correct vehicle speed is updated
                    else:
                        # Since vehicle already exist, update its speed with the new speed
                        
                        if vehicles[expectedSensorPass[i]]["speed"]==-1: # If speed=-1, then the starting lights must be removed
                            removeVehicleStartingLEDs(i-1)
                        
                        if i-1<0: # if this condition is met, then the sensorTime of the previous pi will be required to complete the speed update
                            vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-sensorTime[i-1])
                        else:
                            #*(for now treat it as though there is no previous pi, this line will be removed)
                            vehicles[expectedSensorPass[i]]["speed"]=calcSpeed(sensorsDistance[i],sensorTime[i]-lastPiSensorTime)

                        #Update vision range because speed changed
                        vehicles[expectedSensorPass[i]]["visionRange"]= calcVisionRange(vehicles[expectedSensorPass[i]]["speed"])

                elif state and sensorState[i]==1: # Vehicle is still passing the sensor
                    sensorState[i]=1
                elif state==0 and sensorState[i]==1: # Vehicle has finished passing the sensor
                    sensorState[i]=0
            
            #pass and receive data
            
            #creates cycle if multiple PIs does not exist
            PassToLeadingPi.send()
            PassToTrailingPi.send()
            
            # PI to PI communication
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
