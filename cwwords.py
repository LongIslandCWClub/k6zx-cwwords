#!/usr/bin/env python
# -*- mode: python -*-


import argparse
import inspect
import os
import random
import re
import subprocess
import sys
import time


KOCH_CHARS = ['k', 'm', 'r', 's', 'u', 'a', 'p', 't', 'l', 'o',
              'w', 'i', '.', 'n', 'j', 'e', 'f', '0', 'y', 'v',
              ',', 'g', '5', '/', 'q', '9', 'z', 'h', '3', '8',
              'b', '?', '4', '2', '7', 'c', '1', 'd', '6', 'x']

ENGLISH_WORD_FILE = ["google-10000-english", "google-10000-english-usa.txt"]

EBOOK2CW_INPUT_FILE =  "/tmp/ebook2cwinput.txt"

EBOOK2CW_OUTPUT_BASE = "ebook2cwoutput"
EBOOK2CW_OUTPUT_FILE = os.path.join("/tmp", EBOOK2CW_OUTPUT_BASE)



def parseArguments():
    p = ("Generate mp3 file of Morse Code for code practice. The file contains\n"
         "common English words randomly. The words consist of characters from the "
         "Koch Method of learning Morse Code, the number of Koch letters can be "
         "specified and only words with this set of letters are generated. The "
         "Farnsworth Method is also available and the spacing between charaters "
         "and words may be specified." 
         )

    parser = argparse.ArgumentParser(description='CW Words audio file generator.',
                                      epilog=p)

    parser.add_argument('-c', '--cw-file', action='store', dest='cwFileName',
                        type=str, default="cw.pcm", help='CW PCM output file')
    parser.add_argument('-f', '--freq', action='store', dest='freq', type=int,
                        default=600, help='CW tone frequency (Hz)')
    parser.add_argument('-k', '--koch-chars', action='store', dest='numKochChars',
                        type=int, default=40,
                        help='Number of Koch Method characters to use')
    parser.add_argument('-m', '--max-word-len', action='store', dest='maxWordLen',
                        type=int, default=256,
                        help='Minimum word length')
    parser.add_argument('-n', '--farns-wpm', action='store', dest='farns', type=int,
                        default=5,
                        help='Farnsworth character speed to generate')
    parser.add_argument('-p', '--play', action='store_true', dest='play',
                        help='Play cw word file')
    parser.add_argument('-r', '--random', action='store_true', dest='random',
                        help='Randomize words in the output')
    parser.add_argument('-s', '--min-word-len', action='store', dest='minWordLen',
                        type=int, default=0,
                        help='Minimum word length')
    parser.add_argument('-t', '--tot-words', action='store', dest='totalWords',
                        type=int, default=10000,
                        help='Total number of words to output')
    parser.add_argument('-w', '--wpm', action='store', dest='wpm', type=int,
                        default=20,
                        help='Character speed (words per minute) to generate')

    args = parser.parse_args()

    return args


def getKochChars(numChars):
    return KOCH_CHARS[:numChars]


def getEnglishWordFile():
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))

    wordFile = path
    for p in ENGLISH_WORD_FILE:
        wordFile = os.path.join(wordFile, p)

    # print(f"filename: {wordFile}")
    return wordFile
    

def getWordList(charList):
    wordLst = []
    
    done = False
    with open(getEnglishWordFile(), 'r') as fileobj:

        for line in fileobj:
            word = line.strip()
            # print(f"word: {word}")

            for c in word:
                if c not in charList:
                    break
                else:
                    pass
            else:
                wordLst.append(word)

    return wordLst


def applyMinMax(progArgs, lst):
    wordLst = []
    print(f"min: {progArgs['minWordLen']}")
    print(f"max: {progArgs['maxWordLen']}")

    for word in lst:
        print(f"word: {word} -- len: {len(word)}")
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
           f"-f {progArgs['freq']} -o {EBOOK2CW_OUTPUT_FILE} {EBOOK2CW_INPUT_FILE}")

    proc = subprocess.run(cmd, shell=True, capture_output=False)
    if proc.returncode:
        print(f"ebook2cw return: {proc.returncode}")
    

def playCWSoundFile(wordLst):
    for file in os.listdir('/tmp'):
        if file.find(EBOOK2CW_OUTPUT_BASE) > -1:
            absFile = os.path.join("/tmp", file)
            cmd = f"/usr/bin/mpg123 {absFile}"
            proc = subprocess.run(cmd, shell=True)
            if proc.returncode:
                print(f"mpg123 return: {proc.returncode}")

            time.sleep(2)
            print("words generated:")
            for word in wordLst:
                print(f"{word}", end=" ")

            print("")

            
    

def main():
    args = parseArguments()

    progArgs = {}
    progArgs['numKochChars'] = args.numKochChars
    progArgs['farns'] = args.farns
    progArgs['wpm'] = args.wpm
    progArgs['freq'] = args.freq
    progArgs['totalWords'] = args.totalWords
    progArgs['random'] = args.random
    progArgs['cwFileName'] = args.cwFileName
    progArgs['play'] = args.play
    progArgs['maxWordLen'] = args.maxWordLen
    progArgs['minWordLen'] = args.minWordLen
    print(f"args: {progArgs}")

    charList = getKochChars(progArgs['numKochChars'])
    print(f"chars: {charList}")

    wordLst = getWordList(charList)
    print(f"word list: {wordLst}")
    wordLst = applyMinMax(progArgs, wordLst)
    print(f"word list: {wordLst}")

    if wordLst:
        random.shuffle(wordLst)
        trunWordLst = wordLst[:progArgs['totalWords']]
        print(f"\n\nwords: {trunWordLst}")
        print(f"num words: {len(trunWordLst)}")

        generateCWSoundFile(progArgs, trunWordLst)

        time.sleep(2)
        playCWSoundFile(trunWordLst)
    else:
        print("No words were found using the input parameters, decrease word length")
        print("and/or increase number of characters in set.")

    sys.exit(0)


if __name__ == '__main__':
    main()
