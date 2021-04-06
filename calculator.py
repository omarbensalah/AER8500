import time
import random

altitude = 1200
avionicsUnit = "CHANGEMENT_ALT"
enginePower = 50
verticalSpeed = 1500

while True:
    with open('/tmp/calculatorToInterface', 'w') as f:
        f.write("{},{},{},{}".format(altitude,avionicsUnit,enginePower,verticalSpeed))
        if (random.uniform(0, 1) > 0.75):
            altitude += 100
            enginePower += 2
            verticalSpeed += 100
            avionicsUnit = "AU_SOL"
        else:
            altitude -= 100
            enginePower -= 2
            verticalSpeed -= 100
            avionicsUnit = "CHANGEMENT_ALT"
    time.sleep(0.5)
