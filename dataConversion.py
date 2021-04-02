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

import hashlib

hashList=[]

def insert(source_str, insert_str, pos):
    return ''.join((source_str[:pos], insert_str, source_str[pos:]))

def A429WordToBin(word):
    binStr = str(bin(int(word, 16)))
    while (len(binStr) < 34):
        x = len(binStr)
        binStr = insert(binStr, "0", 2)
    return binStr

def extractLabel(binString): 
    print(binString[-8:][::-1])
    return int("0b" + binString[-8:][::-1], 2)

def encodeLabel(label):
    return format(label,"08b")[::-1]

def extractSsm(binString):
    print(binString[1:4])
    return binString[3:5]    

def decodeAvionicsStatus(binString):
    subStr = binString[22:24]
    print(subStr)
    if subStr=="00":
      return "AU_SOL"
    elif subStr=="01":
      return "CHANGEMENT_ALT"
    elif subStr=="10":
      return "VOL_CROISIERE"

def encodeAvionicsStatus(status):
    if status=="AU_SOL":
	return "00"
    elif status=="CHANGEMENT_ALT":
	return "01"
    elif status=="VOL_CROISIERE":
	return "10"

def decodeBcdBnr(binString, icd):
    val = -int(binString[5]) * icd["range"]
    step = icd["range"] / 2
    for i in range(5, icd["NBS"]):
        val += int(binString[i]) * step
        step /= 2

    return val

def encodeBcd(value,icd):
    value=str(value)
    if icd==2:
	dataString=format(int(value[0]),"03b")+format(int(value[1]),"04b")+format(int(value[2]),"04b")+format(int(value[3]),"04b")+"0000"
    elif icd==3:
        dataString=format(int(value[0]),"03b")+format(int(value[1]),"04b")+format(int(value[2]),"04b")+"00000000"
    return dataString

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
                    return {"avionicsUnit": decodeAvionicsStatus(binString),"altitude": decodeBcdBnr(binString, altitude)}
                else:
                    return "Bad SSM"

        elif label == 2: # Taux de montee BCD
            if ssm == "00":
                return {"verticalSpeed": decodeBcdBnr(binString, verticalSpeed)}
            elif ssm == "11":
                return {"verticalSpeed": -decodeBcdBnr(binString, verticalSpeed)}
            else:
                return {}

        elif label == 3: # Angle d'ataque BCD
            if ssm == "00":
                return {"angleOfAttack": decodeBcdBnr(binString, verticalSpeed)}
            elif ssm == "11":
                return {"angleOfAttack": -decodeBcdBnr(binString, verticalSpeed)}
            else:
                return {}
    
        else:
            return {}

def encodeA429(source,label,status,value):
    if label == 1: # Altitude
	if source == "agr":
	    binString="110"+format(value,"016b")+"0000"+encodeLabel(1)
	elif source == "cal":
	    binString="000"+format(value,"016b")+encodeAvionicsStatus(status)+"00"+encodeLabel(1)
    elif label==2: # Taux de montee
        valueToString=str(abs(value)).zfill(4)
    	if value>0:
	    binString="00"+encodeBcd(valueToString,label)+"00"+encodeLabel(2)
	elif value<0:
	    binString="11"+encodeBcd(valueToString,label)+"00"+encodeLabel(2)
    elif label==3: # Angle d'attaque
        valueToString=str(abs(value)).zfill(3)
    	if value>0:
	    binString="00"+encodeBcd(valueToString,label)+"00"+encodeLabel(3)
	elif value<0:
	    binString="11"+encodeBcd(valueToString,label)+"00"+encodeLabel(3)
    
    # check Parity
    if((binString.count("1") % 2) == 0):
	return "0x{:08x}".format(int("1"+binString,2))
    else:
	return "0x{:08x}".format(int("0"+binString,2))
    
def encodeAFDX(hexString):
    hashList.append(hashlib.md5(hexString.encode()).hexdigest())

def decodeAFDX(hexString):
    hashString=hashlib.md5(hexString.encode()).hexdigest()
    
    if hashString in hashList:
	hashList.remove(hashString)
 

print(decodeA429("0xe0005480", "agr"))
print(encodeLabel(2))
print(encodeA429("cal",2,"CHANGEMENT_ALT",0003))
encodeAFDX("0x80005480")
encodeAFDX("0x80005481")
encodeAFDX("0x80115480")
decodeAFDX("0x80005481")

# use C0, 80 and 40 as first two bytesss
