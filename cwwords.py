#!/usr/bin/env python
# -*- mode: python -*-


# import argparse
import configargparse
import inspect
import os
import random
import re
import subprocess
import sys
import time

from db import *



KOCH_CHARS = ['k', 'm', 'r', 's', 'u', 'a', 'p', 't', 'l', 'o',
              'w', 'i', '.', 'n', 'j', 'e', 'f', '0', 'y', 'v',
              ',', 'g', '5', '/', 'q', '9', 'z', 'h', '3', '8',
              'b', '?', '4', '2', '7', 'c', '1', 'd', '6', 'x']

LOG_DATABASE_FILE = os.path.join(os.environ['HOME'], 'amateur-radio/log-database.db')

# ENGLISH_WORD_FILE = ["google-10000-english", "google-10000-english-usa.txt"]
# ENGLISH_WORD_FILE = ["google-10000-english", "google-10000-english-usa-no-swears.txt"]

EBOOK2CW_INPUT_FILE =  "/tmp/ebook2cwinput.txt"

EBOOK2CW_OUTPUT_BASE = "ebook2cwoutput"
EBOOK2CW_OUTPUT_FILE = os.path.join("/tmp", EBOOK2CW_OUTPUT_BASE)



def parseArguments():
    p = ("Generate CW sound file with English words for code practice. The program "
         "either plays the CW sound file or saves the CW words in an mp3 file. "
         "The words consist of characters from the Koch Method of learning Morse "
         "Code, the number of Koch letters can be "
         "specified and only words with this set of letters are generated. The "
         "Farnsworth Method is also available and the spacing between charaters "
         "and words may be specified." 
         )

    parser = configargparse.ArgumentParser(description='CW Words audio file generator.',
                                      epilog=p)

    parser.add_argument('-c', '--callsigns', action='store_true', dest='callsigns',
                        help='Generate callsigns instead of words')
    parser.add_argument('-d', '--repeat-times', action='store', dest='repeat',
                        type=int, help='Number of times to repeat word')
    parser.add_argument('-f', '--config-file', action='store', dest='configFile',
                        is_config_file=True, help='Config file path')
    parser.add_argument('-k', '--koch-chars', action='store', dest='numKochChars',
                        type=int, default=40,
                        help='Number of Koch Method characters to use')
    parser.add_argument('-m', '--max-word-len', action='store', dest='maxWordLen',
                        type=int, default=256,
                        help='Minimum word length')
    parser.add_argument('-n', '--farns-wpm', action='store', dest='farns', type=int,
                        default=5,
                        help='Farnsworth character speed to generate')
    parser.add_argument('-o', '--sound-file', action='store', dest='mp3Filename',
                        type=str, default=EBOOK2CW_OUTPUT_FILE,
                        help='CW mp3 sound output file')
    parser.add_argument('-p', '--play', action='store_true', dest='play',
                        help='Play cw word file')
    parser.add_argument('-r', '--random', action='store_true', dest='random',
                        help='Randomize words in the output')
    parser.add_argument('-s', '--min-word-len', action='store', dest='minWordLen',
                        type=int, default=0,
                        help='Minimum word length')
    parser.add_argument('-t', '--total-words', action='store', dest='totalWords',
                        type=int, default=10000,
                        help='Total number of words to output')
    parser.add_argument('-u', '--sidetone-freq', action='store', dest='freq',
                        type=int, default=600, help='Sidetone frequency (Hz)')
    parser.add_argument('-w', '--wpm', action='store', dest='wpm', type=int,
                        default=20,
                        help='Character speed (words per minute) to generate')
    parser.add_argument('-x', '--word-file', action='store', dest='wordFile',
                        help='Word file path')
    parser.add_argument('-y', '--call-file', action='store', dest='callsignFile',
                        help='Callsign file path')

    args = parser.parse_args()

    # print("-------------------------------------------------------------------")
    # print(parser.format_help())
    # print("-------------------------------------------------------------------")
    # print(parser.format_values())
    # print("-------------------------------------------------------------------")

    return args


def getKochChars(numChars):
    return KOCH_CHARS[:numChars]


def getLOTWLogCallsigns():
    calllst = []
    logDbase = LogDatabase(LOG_DATABASE_FILE)          # init LogDatabase object
    dbCallLst = logDbase.doDBQuery("select call from callsigndata")

    for call in dbCallLst:
        # print(f"call: {call[0]}")
        calllst.append(call[0])

    return calllst


def removeUSCallsigns(lst):
    resultLst = []

    # All US amateur radio callsigns contain one or two prefix letters
    # beginning with K, N, W, AA-AL, KA-KZ, NA-NZ, or WA-WZ.
    for call in lst:
        if re.search('^[KNW][0-9]', call):
            pass
        elif re.search('^A[A-L][0-9]', call):
            pass
        elif re.search('^K[A-Z][0-9]', call):
            pass
        elif re.search('^N[A-Z][0-9]', call):
            pass
        elif re.search('^W[A-Z][0-9]', call):
            pass
        else:
            resultLst.append(call)
    
    return resultLst
    

def getFCCCallsignList(progArgs):
    callLst = []

    done = False
    with open(progArgs['callsignFile'], 'r') as fileobj:
        for line in fileobj:
            call = line.strip()
            callLst.append(call)

    return callLst


def getCallsignList(progArgs, charList):
    tmpLst = []

    # This function gets callsigns from my LOTW log. This is done to
    # get some foreign callsigns for the training.
    lotwLst = getLOTWLogCallsigns()

    # remove all US callsigns from this list to get just the foreign
    # callsigns
    foreignLst = removeUSCallsigns(lotwLst)

    for call in foreignLst:
        for c in call:
            cl = c.lower()
            if cl not in charList:
                break
            else:
                pass
        else:
            tmpLst.append(call)

    foreignLst = tmpLst

    # This function gets callsigns from FCC datafile stored in a
    # subdirectory. This has many many callsigns but they are all US
    # callsigns.
    fccLst = getFCCCallsignList(progArgs)

    tmpLst = []
    for call in fccLst:
        for c in call:
            cl = c.lower()
            if cl not in charList:
                break
            else:
                pass
        else:
            tmpLst.append(call)

    fccLst = tmpLst

    return fccLst, foreignLst
            
    

# def getEnglishWordFile():
#     filename = inspect.getframeinfo(inspect.currentframe()).filename
#     path = os.path.dirname(os.path.abspath(filename))

#     wordFile = path
#     # for p in ENGLISH_WORD_FILE:
#     for p in 
#         wordFile = os.path.join(wordFile, p)

#     print(f"filename: {wordFile}")
#     return wordFile
    

def getWordList(progArgs, charList):
    wordLst = []
    
    done = False
    # with open(getEnglishWordFile(progArgs), 'r') as fileobj:
    with open(progArgs['wordFile'], 'r') as fileobj:

        for line in fileobj:
            word = line.strip()
            # print(f"word: {word}")

            for c in word:
                if c not in charList:
                    break
                else:
                    pass
            else:
                # print(f"word: {word}")
                wordLst.append(word)

    return wordLst


def applyMinMax(progArgs, lst):
    wordLst = []
    # print(f"min: {progArgs['minWordLen']}")
    # print(f"max: {progArgs['maxWordLen']}")

    for word in lst:
        # print(f"word: {word} -- len: {len(word)}")
        if len(word) < progArgs['minWordLen']:
            pass
        elif len(word) > progArgs['maxWordLen']:
            pass
        else:
            wordLst.append(word)

    return wordLst


def generateCWSoundFile(progArgs, wordLst):
    words = ""

    # write word list to temporary file for input to 'ebook2cw' program
    with open(EBOOK2CW_INPUT_FILE, 'w') as fileobj:
        for word in wordLst:
            fileobj.write(f"{word}\n")

    for file in os.listdir('/tmp'):
        # print(f"file: {file}")
        if file.find(EBOOK2CW_OUTPUT_BASE) > -1 :
            absFile = os.path.join("/tmp", file)
            os.remove(absFile)
            print(f"remove stale mp3 file: {absFile}")

    cmd = (f"/usr/bin/ebook2cw -w {progArgs['wpm']} -e {progArgs['farns']} "
           f"-f {progArgs['freq']} -o {progArgs['mp3Filename']} {EBOOK2CW_INPUT_FILE}")

    # proc = subprocess.run(cmd, shell=True, capture_output=True)
    proc = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode:
        print(f"ebook2cw return: {proc.returncode}")
    for line in proc.stdout.split('\n'):
        # if line.find('ebook2cw') > -1:
        #     print(line)
        if re.search("^ebook2cw", line):
            print(line)
        elif re.search("^Speed", line):
            print(line)
        elif re.search("^Effective", line):
            print(line)
        elif re.search("^Total", line):
            print(line)

            
def removeDuplicates(lst):
    finalLst = []
    for elem in lst:
        if elem not in finalLst:
            finalLst.append(elem)

    return finalLst
    

def playCWSoundFile(wordLst):
    for file in os.listdir('/tmp'):
        if file.find(EBOOK2CW_OUTPUT_BASE) > -1:
            absFile = os.path.join("/tmp", file)
            cmd = f"/usr/bin/mpg123 {absFile}"
            # proc = subprocess.run(cmd, shell=True)
            proc = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            if proc.returncode:
                print(f"mpg123 return: {proc.returncode}")

            time.sleep(2)
            print("---------------------------------------------------------")
            print("words generated:")
            for word in removeDuplicates(wordLst):
                if word == 'vvv':
                    pass
                else:
                    print(f"{word}", end=" ")

            print("")

            
    

def main():
    args = parseArguments()

    progArgs = {}
    progArgs['callsigns'] = args.callsigns
    progArgs['repeat'] = args.repeat
    progArgs['numKochChars'] = args.numKochChars
    progArgs['farns'] = args.farns
    progArgs['wpm'] = args.wpm
    progArgs['freq'] = args.freq
    progArgs['totalWords'] = args.totalWords
    progArgs['random'] = args.random
    progArgs['mp3Filename'] = args.mp3Filename
    progArgs['play'] = args.play
    progArgs['maxWordLen'] = args.maxWordLen
    progArgs['minWordLen'] = args.minWordLen
    progArgs['mp3Filename'] = args.mp3Filename
    if args.wordFile:
        progArgs['wordFile'] = os.path.abspath(args.wordFile)
    if args.callsignFile:
        progArgs['callsignFile'] = os.path.abspath(args.callsignFile)
        
    # print(f"args: {progArgs}")

    charList = getKochChars(progArgs['numKochChars'])
    print(f"Koch characters: {charList}")

    if progArgs['callsigns']:
        print('generate callsigns instead of words')
        fccLst, foreignLst = getCallsignList(progArgs, charList)
        print(f"num FCC calls: {len(fccLst)}, "
              f"num foreign calls: {len(foreignLst)}")

        rnum = random.randint(60, 101) / 100
        fccnum = int(round(progArgs['totalWords'] * rnum))
        fornum = progArgs['totalWords'] - fccnum
        print(f"random num: {rnum}, fcc calls: {fccnum}, "
              f"foreign calls: {fornum}")

        if fccLst:
            random.shuffle(fccLst)
            trunFccLst = fccLst[:progArgs['totalWords']]

            if foreignLst:
                trunFccLst = trunFccLst[:fccnum]

                random.shuffle(foreignLst)
                trunForeignLst = foreignLst[:fornum]

                callsignLst = trunFccLst + trunForeignLst

                random.shuffle(callsignLst)
            else:
                callsignLst = trunFccLst
            
            # if repeat is selected, repeat the words
            if progArgs['repeat']:
                repeatLst = []
                for element in callsignLst:
                    for i in range(progArgs['repeat']):
                        repeatLst.append(element)

                finalCallsignLst = repeatLst

            # Add 'vvv' to beginning of list
            finalCallsignLst.insert(0, 'vvv')
            generateCWSoundFile(progArgs, finalCallsignLst)

            if progArgs['play']:
                time.sleep(2)
                playCWSoundFile(finalCallsignLst)
            else:
                pass
        else:
            print("No callsigns were found using the input parameters, ")
            print("increase number of characters in set.")
                
    else:
        wordLst = getWordList(progArgs, charList)
        # print(f"word list: {wordLst}")
        wordLst = applyMinMax(progArgs, wordLst)
        # print(f"word list: {wordLst}")

        if wordLst:
            random.shuffle(wordLst)
            trunWordLst = wordLst[:progArgs['totalWords']]
            # print(f"\n\nwords: {trunWordLst}")
            # print(f"num words: {len(trunWordLst)}")

            # Add 'vvv' to beginning of list
            trunWordLst.insert(0, 'vvv')
            generateCWSoundFile(progArgs, trunWordLst)

            if progArgs['play']:
                time.sleep(2)
                playCWSoundFile(trunWordLst)
            else:
                pass
        else:
            print("No words were found using the input parameters, decrease word length")
            print("and/or increase number of characters in set.")

    sys.exit(0)


if __name__ == '__main__':
    main()
