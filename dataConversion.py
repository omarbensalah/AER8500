import string
import random

altitude = {
  "NBS": 16,
  "unite": "pieds",
  "range": 65536,
  "resolution": 1
}

enginePower = {
  "NBS": 16,
  "unite": "%",
  "range": 128,
  "resolution": 1
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

ssm_0 = "00"
ssm_3 = "11"

def insert(source_str, insert_str, pos):
    return ''.join((source_str[:pos], insert_str, source_str[pos:]))

def A429WordToBin(word):
    binStr = str(bin(int(word, 16)))
    while (len(binStr) < 34):
        binStr = insert(binStr, "0", 2)

    return binStr

def extractLabel(binString): 
    return int("0b" + binString[-8:][::-1], 2)

def encodeLabel(label):
    return str('{0:08b}'.format(label)[::-1])

def extractSsm(binString):
    return binString[3:5]    

def decodeAvionicsStatus(binString):
    subStr = binString[22:24]
    if subStr == "00":
      return "AU_SOL"
    elif subStr == "01":
      return "CHANGEMENT_ALT"
    elif subStr == "10":
      return "VOL_CROISIERE"

def encodeAvionicsStatus(status):
    if status == "AU_SOL":
	    return "00"
    elif status == "CHANGEMENT_ALT":
	    return "01"
    elif status == "VOL_CROISIERE":
	    return "10"
    else:
        return "11"

def decodeBnr(binString, icd):
    val = -int(binString[5]) * icd["range"]
    step = icd["range"] / 2
    for i in range(0, icd["NBS"]):
        val += int(binString[6 + i]) * step
        step = step / 2

    return val

def decodeBcd(binString,label):
    if label == 2:
        numString = str(int(binString[5:9],2)) + str(int(binString[9:13],2)) + str(int(binString[13:17],2)) + "." + str(int(binString[17:21],2))
    elif label == 3:
        numString = str(int(binString[5:6],2)) + str(int(binString[6:10],2)) + "." + str(int(binString[10:14],2))

    return float(numString)

def encodeBnr(value,icd):
    binString = ""
    step = icd["range"]
    nbs = icd["NBS"]
    
    for x in range(0, nbs + 1):
        if value == 0:
            binString += "0"
            continue
        if step > value:
            binString += "0"
        elif step <= value:
            value -= step
            binString += "1"
        step = step / 2
    
    return binString

def encodeBcd(value,label):
    value = value /1.0
    value = int(value*10)
    if label == 2:
        value = str(value).zfill(4)
        binString = '{0:04b}'.format(int(value[0])) + '{0:04b}'.format(int(value[1])) + '{0:04b}'.format(int(value[2])) + '{0:04b}'.format(int(value[3]))
    elif label == 3:
        value = str(value).zfill(3)
        binString = '{0:01b}'.format(int(value[0])) + '{0:04b}'.format(int(value[1])) + '{0:04b}'.format(int(value[2]))

    return binString.ljust(21,'0')

def decodeA429(word, source):
    if len(word) != 10:
        return {}

    binString = A429WordToBin(word)

    if (binString.count("1") % 2) == 0:
        return "Bad Parity"
    else:    
        label = extractLabel(binString)
        ssm = extractSsm(binString)
        
        if label == 1:
            if source == "agr": # Altitude BNR
                if ssm == "11":
                    return {"altitude": decodeBnr(binString, altitude)}
                else:
                    return "Bad SSM"
            elif source == "cal": # Avionics DIS
                if ssm == "00":
                    return {"avionicsUnit": decodeAvionicsStatus(binString),"altitude": decodeBnr(binString, altitude)}
                else:
                    return "Bad SSM"

        elif label == 2: # Taux de montee BCD
            if ssm == "00":
                return {"verticalSpeed": decodeBcd(binString, label)}
            elif ssm == "11":
                return {"verticalSpeed": -decodeBcd(binString, label)}
            else:
                return {}

        elif label == 3: # Angle d'ataque BCD
            if ssm == "00":
                return {"angleOfAttack": decodeBcd(binString, label)}
            elif ssm == "11":
                return {"angleOfAttack": -decodeBcd(binString, label)}
            else:
                return {}

        if label == 4:
            if ssm == "11":
                return {"enginePower": decodeBnr(binString, enginePower)}
            else:
                return "Bad SSM"

        else:
            return {}

def encodeA429(source, label, status, value):
    if label == 1: # Altitude
        if source == "agr":
            binString = ssm_3 + encodeBnr(value,altitude) + encodeAvionicsStatus(status) + "00" + encodeLabel(1)
        elif source == "cal":
            binString = ssm_0 + encodeBnr(value,altitude) + encodeAvionicsStatus(status) + "00" + encodeLabel(1)

    elif label == 2: # Taux de montee
        if value >= 0:
            binString = ssm_0 + encodeBcd(abs(value),label) + encodeLabel(label)
        elif value < 0:
            binString = ssm_3 + encodeBcd(abs(value),label) + encodeLabel(label)

    elif label == 3: # Angle d'attaque
        if value >= 0:
            binString = ssm_0 + encodeBcd(abs(value),label) + encodeLabel(int(label))
        elif value < 0:
            binString = ssm_3 + encodeBcd(abs(value),label)  + encodeLabel(int(label))

    elif label == 4: # EnginePower
        binString = ssm_3 + encodeBnr(value,enginePower) + encodeAvionicsStatus(status) + "00" + encodeLabel(4)

    
    if ((binString.count("1") % 2) == 0):
        binString = "1" + binString
    else:
        binString="0" + binString

    return '0x{:08x}'.format(int(binString,2)).upper()

def randomHexWord(length):
   letters = "0123456789ABCDEF"
   return ''.join(random.choice(letters) for i in range(length))

def encodeAfdx(source, label, status, value):
    randomPrefix = randomHexWord(50)
    a429World = encodeA429(source, label, status, value)
    suffixPrefix = randomHexWord(17)
    return "0x" + randomPrefix + a429World[2:] + suffixPrefix

def getA429WordFromAfdx(word):
    return word[52:60]

def decodeAfdx(word, source):
    return decodeA429("0x" + word[52:60], source)