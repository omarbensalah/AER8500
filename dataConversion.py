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

def encodeA429(source,label,status,altitude,verticalSpeed,angleOfAttack):
    if label == 1:
	if source == "agr":
	    binString="110"+format(altitude,"016b")+"0000"+encodeLabel(1)
	elif source == "cal":
	    binString="000"+format(altitude,"016b")+encodeAvionicsStatus(status)+"00"+encodeLabel(1)
    #elif label==2:
    	#if verticalSpeed>0:
	    #binString="000"+

    if((binString.count("1") % 2) == 0):
	return hex(int("1"+binString,2))
    else:
	return hex(int("0"+binString,2))
    
def encodeAFDX(hexString):
    f=open("hash.txt","a")
    f.write(hashlib.md5(hexString.encode()).hexdigest()+'\n')
    f.close()

def decodeAFDX(hexString):
    fin=open("hash.txt","r+")
    data=fin.read()
    hashString=hashlib.md5(hexString.encode()).hexdigest()
    if hashString in data:
	data=data.replace(hashString,"")
	fin.close()
    fout=open("hash.txt","w")
    fout.write(data)
    fout.close()
 

print(decodeA429("0xe0005480", "agr"))
print(encodeLabel(2))
print(encodeA429("cal",1,"CHANGEMENT_ALT",5,5,5))
encodeAFDX("0x80005480")
encodeAFDX("0x80005481")
encodeAFDX("0x80115480")
decodeAFDX("0x80005481")

# use C0, 80 and 40 as first two bytesss
