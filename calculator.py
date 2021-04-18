import time
import random
import os
import signal
import errno

altitude = 1200
avionicsUnit = "CHANGEMENT_ALT"
enginePower = 50
verticalSpeed = 1500

requestedAltitude = 0
requestedEnginePower = 0
requestedVerticalSpeed = 0

decodedAltitude = 0
decodedEnginePower = 0
decodedVerticalSpeed = 0

def handleNewRequestedValues(signum, frame):
    try:
        os.mkfifo('/tmp/interfaceToCalculator')
    except OSError as oe: 
        if oe.errno != errno.EEXIST:
            raise

    with open('/tmp/interfaceToCalculator') as fifo:
        while True:
            data = fifo.read()
            if len(data) == 0:
                break
            dataTab = data.split(",")

            if (len(dataTab[0]) == 10): #A429
                decodedAltitude = decodeA429(dataTab[0], "agr")["altitude"]
                decodedEnginePower =  decodeA429(dataTab[1], "agr")["verticalSpeed"]
                decodedVerticalSpeed = decodeA429(dataTab[2], "agr")["enginePower"]
            else:
                decodedAltitude = decodeAfdx(dataTab[0], "agr")["altitude"]
                decodedEnginePower =  decodeAfdx(dataTab[1], "agr")["verticalSpeed"]
                decodedVerticalSpeed = decodeAfdx(dataTab[2], "agr")["enginePower"]
            
            requestedAltitude = int(decodedAltitude) if decodedAltitude != "" else 0
            requestedEnginePower = int(decodedEnginePower) if decodedEnginePower != "" else 0
            requestedVerticalSpeed = int(decodedVerticalSpeed) if decodedVerticalSpeed != "" else 0

            print("New requested values are {}, {}, {}".format(requestedAltitude, requestedEnginePower,requestedVerticalSpeed))

signal.signal(signal.SIGUSR1, handleNewRequestedValues)

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        if (random.uniform(0, 1) > 0.25):
            altitude += 100
            enginePower += 0.1
            verticalSpeed += 100
            avionicsUnit = "AU_SOL"
        else:
            altitude -= 100
            enginePower -= 0.1
            verticalSpeed -= 100
            avionicsUnit = "CHANGEMENT_ALT"

        A429 = "{},{},{}".format(encodeA429("cal", 1, avionicsUnit, altitude), encodeA429("cal", 2, "", verticalSpeed), encodeA429("cal", 3, "", enginePower))
        Afdx = "{},{},{}".format(encodeAfdx("cal", 1, avionicsUnit, altitude), encodeAfdx("cal", 2, "", verticalSpeed), encodeAfdx("cal", 3, "", enginePower))

        if (random.uniform(0, 1) > 0.5):
            f.write(A429 + "," + Afdx)
        else:
            f.write(Afdx + "," + A429)

    time.sleep(0.1)
