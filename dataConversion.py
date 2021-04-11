altitude = {
  "NBS": 16,
  "unite": "pieds",
  "range": 65536,
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

def decodeBnr(binString, icd):
    val = -int(binString[6]) * icd["range"]
    step = icd["range"] / 2.0
    for i in range(6, (icd["NBS"]+6)):
        val += int(binString[i]) * step
        step = step / 2.0

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
    e = icd["resolution"]
    nbs = icd["NBS"]
    if value < 0: #check if negative
        binString += "1"
        value = abs(value)
        if value != step:
            step = step/2.0
            nbs -= 1
        else:
            value -= step
            nbs -= 1
    
    for x in range(1, nbs):
        if value == 0:
            binString += "0"
        if step > value:
            binString += "0"
        elif step < value or abs(step - value) < e :
            value = abs(value)
            value -= step
            binString += "1"
        step = step / 2.0

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
    
        else:
            return {}

def encodeA429(source, label, status, value):
    if label == 1: # Altitude
        if source == "agr":
            binString = "11" + encodeBnr(value,altitude) + encodeAvionicsStatus(status) + "00" + encodeLabel(1)
        elif source == "cal":
            binString = "00" + encodeBnr(value,altitude) + encodeAvionicsStatus(status) + "00" + encodeLabel(1)

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
    
    if ((binString.count("1") % 2) == 0):
        binString = "1" + binString
    else:
        binString="0" + binString
    return '0x{:08x}'.format(int(binString,2))


# print(decodeA429(encodeA429("agr",3,"CHANGEMENT_ALT", 0),"agr"))

# Exhaustive tests for all 3 parameters

for i in range(0, 40000):
    if decodeA429(encodeA429("agr",1,"CHANGEMENT_ALT", i),"agr") == {}:
        print("Error not Equal {}".format(i))

for i in range(-800, 800):
    if decodeA429(encodeA429("agr",2,"CHANGEMENT_ALT", i),"agr")["verticalSpeed"] != i:
        print("Error not Equal {}".format(i))

for i in range(-16, 16):
    if decodeA429(encodeA429("agr",3,"CHANGEMENT_ALT", i),"agr")["angleOfAttack"] != i:
        print("Error not Equal {}".format(i))

# use C0, 80 and 40 as first two bytesss