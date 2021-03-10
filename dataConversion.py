altitude = {
  "NBS": 16,
  "unite": "pieds",
  "range": 65536
}

verticalSpeed = {
  "NBS": 14,
  "unite": "metres/minutes",
  "range": 1024,
  "resolution": 0.0625
}

angleOfAttack = {
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

def decodeAvionicsStatus(binString):
    return

def decodeBcdBnr(binString, icd):
    print(binString[5])
    val = -int(binString[5]) * icd["range"]
    step = icd["range"] / 2
    for i in range(5, icd["NBS"]):
        val += int(binString[i]) * step
        step /= 2

    return val

def decodeA429(word, source):
    if len(word) != 10:
        return {}

    binString = A429WordToBin(word)
    print(binString)

    if (binString.count("1") % 2) == 0:
        return "Bad Parity"
    else:    
        label = extractLabel(binString)
        ssm = extractSsm(binString)
        
        if label == 1:
            if source == "agr": # Altitude BNR
                if ssm == "11":
                    return {"altitude": decodeBcdBnr(binString, altitude)}
                else:
                    return "Bad SSM"
            elif source == "cal": # Avionics DIS
                if ssm == "00":
                    return {"avionicsUnit": decodeAvionicsStatus(binString)}
                else:
                    return "Bad SSM"

        elif label == 2: # Taux de montee BCD
            if ssm == "00":
                return {"verticalSpeed": decodeBcdBnr(binString, verticalSpeed)}
            elif ssm == "11":
                return {"verticalSpeed": - decodeBcdBnr(binString, verticalSpeed)}
            else:
                return {}

        elif label == 3: # Angle d'ataque BCD
            if ssm == "00":
                return {"angleOfAttack": decodeBcdBnr(binString, verticalSpeed)}
            elif ssm == "11":
                return {"angleOfAttack": decodeBcdBnr(binString, verticalSpeed)}
            else:
                return {}


print(decodeA429("0XFE50C180", "agr"))