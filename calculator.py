import time
import random
import os
import signal
import errno

altitude = 0
avionicsUnit = "AU_SOL"
angleOfAttack = 0
verticalSpeed = 0

requestedAltitude = 0
requestedAngleOfAttack = 0
requestedVerticalSpeed = 0

decodedAltitude = 0
decodedAngleOfAttack = 0
decodedVerticalSpeed = 0
APmode = ""

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

            APmode = "AOA" if requestedAngleOfAttack != 0 else "ALT"


signal.signal(signal.SIGUSR1, handleNewRequestedValues)

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        if (APmode == "AOA"):
            avionicsUnit = "VOL_CROISIERE"
            if (requestedAngleOfAttack - angleOfAttack > 1):
                angleOfAttack += 0.1
                avionicsUnit = "CHANGEMENT_ALT"
            elif (requestedAngleOfAttack - angleOfAttack < 1):
                angleOfAttack -= 0.1
                avionicsUnit = "CHANGEMENT_ALT"
            
            verticalSpeed += (requestedVerticalSpeed - verticalSpeed) * 0.167 

        elif (APmode == "ALT"):
            if(requestedAltitude - altitude > 100):
                
            elif(requestedAltitude - altitude < 100):
                verticalSpeed

        altitude += verticalSpeed / 60 * 0.1

        A429 = "{},{},{}".format(encodeA429("cal", 1, avionicsUnit, altitude), encodeA429("cal", 2, "", verticalSpeed), encodeA429("cal", 3, "", angleOfAttack))
        Afdx = "{},{},{}".format(encodeAfdx("cal", 1, avionicsUnit, altitude), encodeAfdx("cal", 2, "", verticalSpeed), encodeAfdx("cal", 3, "", angleOfAttack))

        if (random.uniform(0, 1) > 0.5):
            f.write(A429 + "," + Afdx)
        else:
            f.write(Afdx + "," + A429)
        
    time.sleep(0.1)
