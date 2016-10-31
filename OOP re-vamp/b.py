from firebase import firebase
import datetime
import ast
import os
import pickle
import time
import threading
# import serverEnd
# import serverStart
# import clientEnd
# import clientStart
import datetime
import time
import calendar
# import RPi.GPIO as GPIO
from EmulatorGUI import GPIO

class Sensor():
    def __init__(self):
        self._pin=0#--
        self._state=0
        self._time=0
        self._expectedSensorPass=-1
        self._distance=0
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value


    @property
    def expectedSensorPass(self):
        return self._expectedSensorPass

    @expectedSensorPass.setter
    def expectedSensorPass(self, value):
        self._expectedSensorPass = value


    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

class Sensors:  
    def __init__(self,sensorsToAdd):
        self._sensors=[]
        for i in range(0,len(sensorsToAdd)):
            self.addNewSensor(sensorsToAdd[i])
        
    @property
    def sensor(self):
        return self._sensor

    @sensor.setter
    def sensor(self, value):
        self._sensors = value
        
    def addNewSensor(self, pin):
        self._sensors.append(Sensor(pin))
        
    def getSensor(self,i):
        return self._sensors[i]
        
    def numSensors(self):
        return len(self._sensors)
        
    # Sets the distance between all sensors to be of even distance which is received as an argument
    def setAllsensorsDistance(self,dist):
        for i in range(0,self.numSensors()):
            self._sensors[i].distance=dist

class Led:
    def __init__(self,pin):
        self._pin=0#--
        self._state=0
        self._stateNew=0
        self._distance=0
        
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value


    @property
    def stateNew(self):
        return self._stateNew

    @stateNew.setter
    def stateNew(self, value):
        self._stateNew = value


    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value
        
class Leds:
    def __init__(self,ledsToAdd):
        self._leds=[]
        for i in range(0,len(ledsToAdd)):
            self.addNewLeds(ledsToAdd[i])
        
    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value
        
    def numLeds(self):
        return len(self._leds)
        
    def addNewLeds(self,pin):
        self._leds.append(Led(pin))
        
    def getLed(self,i):
        return self._leds[i]
        
    # Based on the amount of LEDs that are controlled by the PI, the LEDs distance is calculated evenly based on the sensors distance(most likely set by the function above)
    def setAllLEDsDistance(sensors,LEDsMult):
        for i in range(0,sensors.numSensors()):
            if i==0:
                dist=sensors.getSensor(i).distance
                avg=dist/LEDsMult
            else:
                dist=sensors.getSensor(i).distance
                avg=dist/LEDsMult
            
            for j in range(i*LEDsMult,((i+1)*LEDsMult)):
                self._leds[j].distance(avg)
    


class Vehicle():
    def __init__(self):
        self._currentPos=0
        self._timePlaced=0
        self._speed=0
        self._visionRange=0
        self._maxSpeed=0
        self._sensorspassed=0
        self._avgSpeed=0
        
    @property
    def currentPos(self):
        return self._currentPos

    @currentPos.setter
    def currentPos(self, value):
        self._currentPos = value


    @property
    def timePlaced(self):
        return self._timePlaced

    @timePlaced.setter
    def timePlaced(self, value):
        self._timePlaced = value


    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value


    @property
    def visionRange(self):
        return self._visionRange

    @visionRange.setter
    def visionRange(self, value):
        self._visionRange = value


    @property
    def maxSpeed(self):
        return self._maxSpeed

    @maxSpeed.setter
    def maxSpeed(self, value):
        self._maxSpeed = value


    @property
    def sensorspassed(self):
        return self._sensorspassed

    @sensorspassed.setter
    def sensorspassed(self, value):
        self._sensorspassed = value


    @property
    def avgSpeed(self):
        return self._avgSpeed

    @avgSpeed.setter
    def avgSpeed(self, value):
        self._avgSpeed = value

class Vehicles:
    def __init__(self):
        self._vehicles=[]
        
    @property
    def vehicle(self):
        return self._vehicle

    @vehicle.setter
    def vehicle(self, value):
        self._vehicle = value
        
    def addNewVehicles(self):
        self._vehicles.append(Vehicle())
        
    def getVehicle(self,i):
        return self._vehicles[i]
        
class LeadingData:
    def __init__(self):
        self._light=0
        self._fade=0
        self._newVehicle=0
        self._expectedSensorUpdate=0
        self._lastSensorTime=0
        
    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        self._light = value


    @property
    def fade(self):
        return self._fade

    @fade.setter
    def fade(self, value):
        self._fade = value


    @property
    def newVehicle(self):
        return self._newVehicle

    @newVehicle.setter
    def newVehicle(self, value):
        self._newVehicle = value


    @property
    def expectedSensorUpdate(self):
        return self._expectedSensorUpdate

    @expectedSensorUpdate.setter
    def expectedSensorUpdate(self, value):
        self._expectedSensorUpdate = value


    @property
    def lastSensorTime(self):
        return self._lastSensorTime

    @lastSensorTime.setter
    def lastSensorTime(self, value):
        self._lastSensorTime = value

class TrailingData():
    def __init__(self):
        self._light=0
        self._fade=0

    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, value):
        self._light = value


    @property
    def fade(self):
        return self._fade

    @fade.setter
    def fade(self, value):
        self._fade = value

class firebaseSys:
    def __init__(self):
        self._id=0
        self._avgSpeed=0
        self._numOfNewCars=0
        self._LEDsTurnedOn=0
        
        # Firebase =firebase.FirebaseApplication('https://prog-c99a8.firebaseio.com/')
        Firebase =firebase.FirebaseApplication('https://slight-91c01.firebaseio.com/')
    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value


    @property
    def avgSpeed(self):
        return self._avgSpeed

    @avgSpeed.setter
    def avgSpeed(self, value):
        self._avgSpeed = value


    @property
    def numOfNewCars(self):
        return self._numOfNewCars

    @numOfNewCars.setter
    def numOfNewCars(self, value):
        self._numOfNewCars = value


    @property
    def LEDsTurnedOn(self):
        return self._LEDsTurnedOn

    @LEDsTurnedOn.setter
    def LEDsTurnedOn(self, value):
        self._LEDsTurnedOn = value
    
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
        
class System:
    def __init__(self):
        self._leds=Leds([15,18,23,24,8,7,12,16,21,26,19,13,5,11,9,10,27,17,4,3])
        self._sensors=Sensors([14,25,20,6,22])
        #self._leds=Leds([16,12,17,27,5,20,19,21])
        #self._sensors=Sensors([23,18])
        self._firebaseSys
        self._passToLeadingPi
        self._receiveFromLeadingPi
        self._passToTrailingPi
        self._receiveFromTrailingPi
        
    @property
    def leds(self):
        return self._leds

    @leds.setter
    def leds(self, value):
        self._leds = value

    
    @property
    def sensors(self):
        return self._sensors

    @sensorspassed.setter
    def sensors(self, value):
        self._sensors = value


    @property
    def firebaseSys(self):
        return self._firebaseSys

    @firebaseData.setter
    def firebaseSys(self, value):
        self._firebaseSys = value


    @property
    def passToLeadingPi(self):
        return self._passToLeadingPi

    @passToLeadingPi.setter
    def passToLeadingPi(self, value):
        self._passToLeadingPi = value


    @property
    def receiveFromLeadingPi(self):
        return self._receiveFromLeadingPi

    @receiveFromLeadingPi.setter
    def receiveFromLeadingPi(self, value):
        self._receiveFromLeadingPi = value


    @property
    def passToTrailingPi(self):
        return self._passToTrailingPi

    @passToTrailingPi.setter
    def passToTrailingPi(self, value):
        self._passToTrailingPi = value


    @property
    def receiveFromTrailingPi(self):
        return self._receiveFromTrailingPi

    @receiveFromTrailingPi.setter
    def receiveFromTrailingPi(self, value):
        self._receiveFromTrailingPi = value

    def setGPIO(system):
        GPIO.setmode(GPIO.BCM) # Set GPIO mode for pi
        
        # Sets the GPIO Pins of the PI's sensors to send input to PI 
        for i in range(0,len(sensors)):
            GPIO.setup(self._sensors.getSensor(i).pin,GPIO.IN)
            
        # Sets the GPIO Pins of the PI's LEDs to receive output from the PI 
        for i in range(0,len(LEDS)):
            GPIO.setup(self._leds.getLed(i).pin,GPIO.OUT)
        
    # Turns on associated Light by the index number passed 
    def lighton(i):
        GPIO.output(self._leds.getLed(i).pin,GPIO.HIGH)

    # Turns off associated Light by the index number passed
    def lightoff(i):
        GPIO.output(self._leds.getLed(i).pin,GPIO.LOW)
        
    # Function used to detect if an object has passed the sensor or not
    def scan(S): 
        curr= GPIO.input(S)
        if curr !=0: # For python 3.5
        # if curr ==0: # For python 2.7
            return S    
        else:     
            return 0
        
def main():
    try:
        system=System()
        system.setGPIO()
        
    except KeyboardInterrupt:
            run = False
    finally:
        GPIO.cleanup();
        
if __name__ == "__main__": 
    main()