#!/usr/bin/env python
# -*- mode: python -*-


# Simple program that reads the AM.dat file downloaded from the FCC
# and removes all fields except the callsign. 

import os.path
import sys

CALLSIGN_FILENAME = "am.dat"


def main():
    print("args: ", str(sys.argv))

    fccDataFile = os.path.abspath(sys.argv[1])
    print(f"fccDataFile: {fccDataFile}")

    dataDir = os.path.dirname(fccDataFile)
    print(f"dir: {dataDir}")

    callsignFile = os.path.join(dataDir, CALLSIGN_FILENAME)
    print(f"callsign file: {callsignFile}")

    try:
        fp = open(fccDataFile, 'r')
        op = open(callsignFile, 'w')

        for cnt, line in enumerate(fp):
            lin = line.strip()
            # print(f"cnt: {cnt} - line: {lin}")

            callsign = lin.split('|')[4]
            # print(f"callsign: {callsign}")
            op.write(f"{callsign}\n")

        fp.close()
        op.close()


    except IOError:
        print(f"File is not accessible: {fccDataFile}")
        
    


if __name__ == '__main__':
    main()
