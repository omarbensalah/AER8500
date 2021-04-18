import math

def findAngleOfAttack(enginePower,verticalSpeed):
    return math.degrees(math.asin(verticalSpeed / (enginePower * 12)))
