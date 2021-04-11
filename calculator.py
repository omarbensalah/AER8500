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
            requestedAltitude = int(dataTab[0]) if dataTab[0] != "" else 0
            requestedEnginePower = int(dataTab[1]) if dataTab[1] != "" else 0
            requestedVerticalSpeed = int(dataTab[2]) if dataTab[2] != "" else 0

    print("New values are {}, {}, {}".format(requestedAltitude, requestedEnginePower,requestedVerticalSpeed))

signal.signal(signal.SIGUSR1, handleNewRequestedValues)

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        f.write("{},{},{},{}".format(altitude,enginePower,verticalSpeed,avionicsUnit))
        if (random.uniform(0, 1) > 0.25):
            altitude += 100
            enginePower += 2
            verticalSpeed += 100
            avionicsUnit = "AU_SOL"
        else:
            altitude -= 100
            enginePower -= 2
            verticalSpeed -= 100
            avionicsUnit = "CHANGEMENT_ALT"
    time.sleep(0.1)
