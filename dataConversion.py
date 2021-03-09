altitude = {
  "MSB": 28,
  "NBS": 16,
  "unite": "pieds",
  "range": 65536
}

verticalSpeed = {
  "MSB": 28,
  "NBS": 14,
  "unite": "metres/minutes",
  "range": 1024,
  "resolution": 0.0625
}

angleOfAttack = {
  "MSB": 28,
  "NBS": 9,
  "unite": "degres",
  "range": 32,
  "resolution": 0.0625
}

def A429WordToBin(word):
    return str(bin(int(word, 16)))

def extractLabel(binString): 
    return int("0b" + binString[-8:][::-1], 2)

def extractSsm(binString):
    return binString[2:4]    

def decodeAltitude(binString):
    return

def decodeAvionicsStatus(binString):
    return

def decodeVerticalSpeed(binString):
    return

def 


def decodeA429(word, source):
    binString = A429WordToBin(word)
    print(binString)
    if (binString.count("1") % 2) == 0:
        return 
    else:    
        output = {}
        label = extractLabel(binString)
        ssm = extractSsm(binString)
        
        if label == 1:
            if source == "agr": # Altitude BNR
                if ssm == "11":
                    decodeAltitude(binString)
                else:
                    return
            elif source == "cal": # Avioncs DIS
                if ssm == "00":
                    decodeAvionicsStatus(binString)
                else:
                    return
        elif label == 2: # Taux de montee BCD
            if ssm == "00":
                decodeVerticalSpeed(binString)
            elif ssm == "11":
                decodeVerticalSpeed(binString)
            else:
                return
        elif label == 3: # Angle d'ataque BCD
            if ssm == "00":
                decodeAngleOfAttack(binString)
            elif ssm == "11":
                decodeAngleOfAttack(binString)
            else:
                return
                
    return output




decodeA429("0XA750C143", "agr")