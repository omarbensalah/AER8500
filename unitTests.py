from dataConversion import encodeA429
from dataConversion import decodeA429

# Exhaustive tests for all 3 parameters
count = 0

for i in range(0, 40000):
    if decodeA429(encodeA429("agr",1,"CHANGEMENT_ALT", i),"agr")["altitude"] != i:
        count += 1
        print("Error not Equal {}".format(i))
    
print("Altitude count {}".format(count))

for i in range(-800, 800):
    if decodeA429(encodeA429("agr",2,"CHANGEMENT_ALT", i),"agr")["verticalSpeed"] != i:
        count += 1
        print("Error not Equal {}".format(i))

print("Vertical Speed count {}".format(count))


for i in range(-16, 16):
    if decodeA429(encodeA429("agr",3,"CHANGEMENT_ALT", i),"agr")["angleOfAttack"] != i:
        count += 1
        print("Error not Equal {}".format(i))

print("Angle Of Attack count {}".format(count))