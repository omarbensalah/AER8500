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
    val = -int(binString[6]) * icd["range"]
    step = icd["range"] / 2
    for i in range(6, (icd["NBS"]+6)):
        val += int(binString[i]) * step
        step =step/ 2

    return val

def encodeBcdBnr(value,icd):
    
    binString=""
    step=icd["range"]
    for x in range(1,icd["NBS"]):
        
        if value==0:
            binString+="0"
        if step > value:
            binString+="0"
        elif step <=value:
            value-=step
            binString+="1"
        step=step/2
    return binString



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
            binString="11"+encodeBcdBnr(value,altitude)+encodeAvionicsStatus(status)+"00"+encodeLabel(1)
        elif source == "cal":
            binString="00"+encodeBcdBnr(value,altitude)+encodeAvionicsStatus(status)+"00"+encodeLabel(1)
    elif label==2: # Taux de montee
        
        if value>0:
            binString="00"+encodeBcdBnr(abs(value),verticalSpeed)+"00"+encodeLabel(2)
        elif value<0:
            binString="11"+encodeBcdBnr(abs(value),verticalSpeed)+"00"+encodeLabel(2)
    elif label==3: # Angle d'attaque
        
        if value>0:
            binString="00"+encodeBcdBnr(abs(value),angleOfAttack)+"00"+encodeLabel(3)
        elif value<0:
            binString="11"+encodeBcdBnr(abs(value),angleOfAttack)+"00"+encodeLabel(3)
    print(binString)
    # check Parity
    if((binString.count("1") % 2) == 0):
        binString="1"+binString
        return hex(int(binString,2))
    else:
        binString="0"+binString
        return hex(int(binString,2))
    
def encodeAFDX(hexString):
    hashList.append(hashlib.md5(hexString.encode()).hexdigest())

def decodeAFDX(hexString):
    hashString=hashlib.md5(hexString.encode()).hexdigest()
    
    if hashString in hashList:
        hashList.remove(hashString)
 


print(decodeA429(encodeA429("cal",1,"CHANGEMENT_ALT",1200),"cal"))
#print(encodeBnr(1200,altitude))
print(decodeA429("0x804b0480","cal"))


# use C0, 80 and 40 as first two bytesss
