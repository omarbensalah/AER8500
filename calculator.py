import time
import random
import os
import signal
import errno

altitude = 1200
avionicsUnit = "CHANGEMENT_ALT"
angleOfAttack = 50
verticalSpeed = 1500

requestedAltitude = 0
requestedAngleOfAttack = 0
requestedVerticalSpeed = 0

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

            decodedAltitude = decodeA429(dataTab[0], "agr")["altitude"]
            decodedAngleOfAttack =  decodeA429(dataTab[1], "agr")["verticalSpeed"]
            decodedVerticalSpeed = decodeA429(dataTab[2], "agr")["angleOfAttack"]
            
            requestedAltitude = int(decodedAltitude) if decodedAltitude != "" else 0
            requestedAngleOfAttack = int(decodedAngleOfAttack) if decodedAngleOfAttack != "" else 0
            requestedVerticalSpeed = int(decodedVerticalSpeed) if decodedVerticalSpeed != "" else 0

    print("New requested values are {}, {}, {}".format(requestedAltitude, requestedAngleOfAttack,requestedVerticalSpeed))

signal.signal(signal.SIGUSR1, handleNewRequestedValues)

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        if (random.uniform(0, 1) > 0.25):
            altitude += 100
            angleOfAttack += 0.1
            verticalSpeed += 100
            avionicsUnit = "AU_SOL"
        else:
            altitude -= 100
            angleOfAttack -= 0.1
            verticalSpeed -= 100
            avionicsUnit = "CHANGEMENT_ALT"

        encodedAltitude = encodeA429("cal", 1, avionicsUnit, altitude)
        encodedAngleOfAttack = encodeA429("cal", 2, "", angleOfAttack)
        encodedVerticalSpeed = encodeA429("cal", 3, "", verticalSpeed)

        f.write("{},{},{}".format(encodedAltitude, encodedAngleOfAttack, encodedVerticalSpeed))
    time.sleep(0.1)
