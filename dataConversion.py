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
preamble="A202011A202011"
frameDelimiter="AB"
destAddress="313144313144"
sourceAddress="515166515166"
ipV4="BBBB"
ipAdress="00221313BCD00221313BCD00221313BC7070F0A0"
udp="CDE0606F0A03636A"
frameCheck="10101010"
frameGap="EEEEEEEEEEEEEEEEEEEEEEEE"


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
                    return {"avionicsUnit": decodeAvionicsStatus(binString)}
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

def encodeA429(word):
    return hex(int(word,2))


print(decodeA429("0x80000880", "cal"))
print(encodeA429("10000000000000000000100010000000"))

# use C0, 80 and 40 as first two bytesss
