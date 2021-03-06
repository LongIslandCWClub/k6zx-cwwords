#!/usr/bin/env python
# -*- mode: python -*-



import os
import re
import string
import sys
import time

from qrz import *


QRZ_USERNAME   = 'K6ZX'
QRZ_PASSWORD   = 'Sean!12233'

# FOREIGN_CALL_FILE = os.path.join(os.environ['HOME'],
#                                  'local/deploy/cwwords/database/foreign.dat')
FOREIGN_CALL_FILE = os.path.join(os.environ['HOME'],
                                 'devel/python/cwwords-data/foreign.dat')

NUM_DOTS = 0


def getCalldata(call):
    global NUM_DOTS
    
    result = "notfound"
    
    if re.search('.*[0-9]+.*', call):
        # callsigns need at least one number
        # so check for that
    
        while True:
            try:
                qrz = QRZ(QRZ_USERNAME, QRZ_PASSWORD)
                c = qrz.callsignData(call, verbose=False)
                # print(f"DEBUG callsignData(): {c}")
                if c['country'] != 'United States':
                    result = (f"{c['call']}|{c['fname']}|{c['name']}|{c['addr1']}|"
                              f"{c['addr2']}|{c['country']}|{call}")
                    break
                else:
                    break
            except CallsignNotFound as e:
                # print(f"getCalldata() {e}")
                break
            except KeyError:
                break
            except AttributeError:
                break
            except Exception as e:
                # print("", end="\r")               # carriage return
                # sys.stdout.write("\033[K")        # clear to EOL
                # NUM_DOTS = 0
                print(f"\nWARNING: {e}")
                time.sleep(60)

        time.sleep(1)      # slow the QRZ query rate down
                
    columns, rows = os.get_terminal_size(0)
    columns -= 5
    if result == "notfound":
        if NUM_DOTS >= columns:
            # goto beginning of line and clear it
            print("", end="\r")               # carriage return
            sys.stdout.write("\033[K")        # clear to EOL
            NUM_DOTS = 0
        else:
            print('.', end="", flush=True)
            NUM_DOTS += 1
    else:
        # a callsign was found so clear to EOL so that the data can be
        # printed (by another function)
        if NUM_DOTS > 0:
            print("", end="\r")
            sys.stdout.write("\033[K")
            NUM_DOTS = 0
            
    return result
        


def getStartingCallsign():
    callsign = ""

    if os.path.exists(FOREIGN_CALL_FILE):
        print(f"getStartingCallsign(): file {FOREIGN_CALL_FILE} exists")
        with open(FOREIGN_CALL_FILE, 'r') as fileobj:
            for line in fileobj:
                l = line.strip()
                call = l.split("|")[0]
                # print(f"    {call}")

            # print(f"getStartingCallsign(): {call}")

        callsign = call
        
    return callsign


def generateCallsigns(startCall):
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
            
    with open(FOREIGN_CALL_FILE, 'a') as fileobj:
        if restartCallLen <= 4:
            # generate 4 character callsigns
            print("Getting 4 character callsigns")
            for a in aStr:
                for b in bStr:
                    for c in cStr:
                        for d in dStr:
                            call = f"{a}{b}{c}{d}"
                            callData = getCalldata(call)

                            if not re.search("notfound", callData):
                                print(f"{callData}")
                                fileobj.write(f"{callData}\n")
                                fileobj.flush()
                                os.sync()

            # generate 5 character callsigns
            print("Getting 5 character callsigns")
            for a in string.ascii_uppercase + string.digits:
                for b in string.ascii_uppercase + string.digits:
                    for c in string.ascii_uppercase + string.digits:
                        for d in string.ascii_uppercase + string.digits:
                            for e in string.ascii_uppercase + string.digits:
                                call = f"{a}{b}{c}{d}{e}"
                                callData = getCalldata(call)

                                if not re.search("notfound", callData):
                                    print(f"{callData}")
                                    fileobj.write(f"{callData}\n")
                                    fileobj.flush()
                                    os.sync()

            # generate 6 character callsigns
            print("Getting 6 character callsigns")
            for a in string.ascii_uppercase + string.digits:
                for b in string.ascii_uppercase + string.digits:
                    for c in string.ascii_uppercase + string.digits:
                        for d in string.ascii_uppercase + string.digits:
                            for e in string.ascii_uppercase + string.digits:
                                for f in string.ascii_uppercase + string.digits:
                                    call = f"{a}{b}{c}{d}{e}{f}"
                                    callData = getCalldata(call)

                                    if not re.search("notfound", callData):
                                        print(f"{callData}")
                                        fileobj.write(f"{callData}\n")
                                        fileobj.flush()
                                        os.sync()

                                        

def main():
    # qrz = QRZ(QRZ_USERNAME, QRZ_PASSWORD)

    startingCall = getStartingCallsign()
    print(f"starting callsign: {startingCall}")

    # generateCallsigns(qrz, startingCall)
    generateCallsigns(startingCall)

    


                        
    
if __name__ == '__main__':
    main()
