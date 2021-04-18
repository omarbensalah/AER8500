import time
import random
import os
import signal
import math
import errno

altitude = 0
avionicsUnit = "AU_SOL"
angleOfAttack = 0
verticalSpeed = 0
enginePower = 0
totalSpeed = 0
APmode = ""

requestedAltitude = 0
requestedAngleOfAttack = 0
requestedVerticalSpeed = 0


def handleNewRequestedValues(signum, frame):
    try:
        os.mkfifo('/tmp/interfaceToCalculator')
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

    global APmode, requestedAltitude, requestedAngleOfAttack, requestedVerticalSpeed

    with open('/tmp/interfaceToCalculator') as fifo:
        while True:
            data = fifo.read()
            if len(data) == 0:
                break
            dataTab = data.split(",")

            if (len(dataTab[0]) == 10): #A429
                decodedAltitude = decodeA429(dataTab[0], "agr")["altitude"]
                decodedAngleOfAttack =  decodeA429(dataTab[1], "agr")["angleOfAttack"]
                decodedVerticalSpeed = decodeA429(dataTab[2], "agr")["verticalSpeed"]
            else:
                decodedAltitude = decodeAfdx(dataTab[0], "agr")["altitude"]
                decodedAngleOfAttack =  decodeAfdx(dataTab[1], "agr")["angleOfAttack"]
                decodedVerticalSpeed = decodeAfdx(dataTab[2], "agr")["verticalSpeed"]
            
            requestedAltitude = int(decodedAltitude) if decodedAltitude != "" else 0
            requestedAngleOfAttack = float(decodedAngleOfAttack) if decodedAngleOfAttack != "" else 0
            requestedVerticalSpeed = int(decodedVerticalSpeed) if decodedVerticalSpeed != "" else 0

            APmode = "ALT" if requestedAltitude != 0 else "AOA"

signal.signal(signal.SIGUSR1, handleNewRequestedValues)

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        if (APmode == "AOA"):
            if (requestedAngleOfAttack - angleOfAttack > 1):
                angleOfAttack += 0.1
                
            elif (requestedAngleOfAttack - angleOfAttack < 1):
                angleOfAttack -= 0.1
                
            avionicsUnit = "CHANGEMENT_ALT"
            verticalSpeed += (requestedVerticalSpeed - verticalSpeed) * 0.167 

            enginePower = requestedVerticalSpeed / (math.sin(math.radians(requestedAngleOfAttack)) * 10)

        elif (APmode == "ALT"):
            if(requestedAltitude - altitude > 100):
                if(enginePower > 80):
                    enginePower -= 2
                else:
                    enginePower += 2
                if(verticalSpeed > 600):
                    verticalSpeed -= 100
                elif(verticalSpeed<600):
                    verticalSpeed += 100
                
            elif(requestedAltitude - altitude < 100):
                if(enginePower > 80):
                    enginePower -= 2
                else:
                    enginePower += 2
                if(verticalSpeed > 600):
                    verticalSpeed -= 100
                elif(verticalSpeed<600):
                    verticalSpeed += 100
                
            avionicsUnit = "CHANGEMENT_ALT"
            

        altitude += verticalSpeed / 60 * 0.1

        A429 = "{},{},{},{}".format(encodeA429("cal", 1, avionicsUnit, altitude), encodeA429("cal", 2, "", verticalSpeed), encodeA429("cal", 3, "", angleOfAttack), encodeA429("cal", 4, "", enginePower))
        Afdx = "{},{},{},{}".format(encodeAfdx("cal", 1, avionicsUnit, altitude), encodeAfdx("cal", 2, "", verticalSpeed), encodeAfdx("cal", 3, "", angleOfAttack), encodeAfdx("cal", 4, "", enginePower))

        if (random.uniform(0, 1) > 0.5):
            f.write(A429 + "," + Afdx)
        else:
            f.write(Afdx + "," + A429)
        
    time.sleep(1)
