#!/usr/bin/env python
# -*- mode: python -*-


import os
import string
import sys
import time

from qrz import *


QRZ_USERNAME   = 'K6ZX'
QRZ_PASSWORD   = 'Sean!12233'

FOREIGN_CALL_FILE = os.path.join(os.environ['HOME'],
                                 'local/deploy/cwwords/database/foreign.dat')


def getCalldata(qrz, call):
    result = "notfound"
    
    try:
        c = qrz.callsignData(call, verbose=False)
        if c['country'] == 'United States':
            pass
        else:
            result = (f"{c['call']}|{c['fname']}|{c['name']}|{c['addr1']}|"
                      f"{c['addr2']}|{c['country']}")
    except CallsignNotFound:
        pass
    except KeyError:
        pass
    except AttributeError:
        pass

    time.sleep(4)      # slow the QRZ query rate down
    
    return result
        


def getStartingCallsign():
    callsign = ""

    if os.path.exists(FOREIGN_CALL_FILE):
        with open(FOREIGN_CALL_FILE, 'r') as fileobj:
            for line in fileobj:
                call = line.split("|")[0]

        callsign = call
        
    return callsign


def generateCallsigns(qrz, startCall):
    print(f"generateCallsigns() call: {startCall}")

    aStr = string.ascii_uppercase + string.digits
    bStr = string.ascii_uppercase + string.digits
    cStr = string.ascii_uppercase + string.digits
    dStr = string.ascii_uppercase + string.digits
    eStr = string.ascii_uppercase + string.digits
    fStr = string.ascii_uppercase + string.digits
    
    restartCallLen = 0
    if startCall != "":
        restartCallLen = len(startCall)
        print(f"call len : {restartCallLen}")

        for i in range(len(string.ascii_uppercase + string.digits)):
            if startCall[0] == aStr[i]:
                break
        aStr = aStr[i + 1:]

        for i in range(len(string.ascii_uppercase + string.digits)):
            if startCall[1] == bStr[i]:
                break
        bStr = bStr[i + 1:]

        for i in range(len(string.ascii_uppercase + string.digits)):
            if startCall[2] == cStr[i]:
                break
        cStr = cStr[i + 1:]

        for i in range(len(string.ascii_uppercase + string.digits)):
            if startCall[3] == dStr[i]:
                break
        dStr = dStr[i + 1:]

        print(f"debug: aStr {aStr}")
        print(f"debug: bStr {bStr}")
        print(f"debug: cStr {cStr}")
        print(f"debug: dStr {dStr}")

        if restartCallLen >= 5:
            for i in range(len(string.ascii_uppercase + string.digits)):
                if startCall[4] == eStr[i]:
                    break
            eStr = eStr[i + 1:]

            print(f"debug: eStr {eStr}")

        if restartCallLen >= 6:
            for i in range(len(string.ascii_uppercase + string.digits)):
                if startCall[5] == fStr[i]:
                    break
            fStr = fStr[i + 1:]

            print(f"debug: fStr {fStr}")
            
    with open(FOREIGN_CALL_FILE, 'w') as fileobj:
        if restartCallLen <= 4:
            # generate 4 character callsigns
            print("Getting 4 character callsigns")
            for a in aStr:
                for b in bStr:
                    for c in cStr:
                        for d in dStr:
                            call = f"{a}{b}{c}{d}"
                            callData = getCalldata(qrz, call)

                            if callData != "notfound":
                                print(f"{callData}")
                                fileobj.write(f"{callData}\n")

            # generate 5 character callsigns
            print("Getting 5 character callsigns")
            for a in string.ascii_uppercase + string.digits:
                for b in string.ascii_uppercase + string.digits:
                    for c in string.ascii_uppercase + string.digits:
                        for d in string.ascii_uppercase + string.digits:
                            for e in string.ascii_uppercase + string.digits:
                                call = f"{a}{b}{c}{d}{e}"
                                callData = getCalldata(qrz, call)

                                if callData != "notfound":
                                    print(f"{callData}")
                                    fileobj.write(f"{callData}\n")

            # generate 6 character callsigns
            print("Getting 6 character callsigns")
            for a in string.ascii_uppercase + string.digits:
                for b in string.ascii_uppercase + string.digits:
                    for c in string.ascii_uppercase + string.digits:
                        for d in string.ascii_uppercase + string.digits:
                            for e in string.ascii_uppercase + string.digits:
                                for f in string.ascii_uppercase + string.digits:
                                    call = f"{a}{b}{c}{d}{e}{f}"
                                    callData = getCalldata(qrz, call)

                                    if callData != "notfound":
                                        print(f"{callData}")
                                        fileobj.write(f"{callData}\n")

                                        

def main():
    qrz = QRZ(QRZ_USERNAME, QRZ_PASSWORD)

    startingCall = getStartingCallsign()

    generateCallsigns(qrz, startingCall)

    


                        
    
if __name__ == '__main__':
    main()
