#!/usr/bin/env python
# -*- mode: python -*-


import argparse
import inspect
import os
import re
import sys


KOCH_CHARS = ['k', 'm', 'r', 's', 'u', 'a', 'p', 't', 'l', 'o',
              'w', 'i', '.', 'n', 'j', 'e', 'f', '0', 'y', 'v',
              ',', 'g', '5', '/', 'q', '9', 'z', 'h', '3', '8',
              'b', '?', '4', '2', '7', 'c', '1', 'd', '6', 'x']

ENGLISH_WORD_FILE = ["google-10000-english", "google-10000-english-usa.txt"]



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

    parser.add_argument('-f', '--freq', action='store', dest='freq', type=int,
                        default=600, help='CW tone frequency (Hz)')
    parser.add_argument('-k', '--koch-chars', action='store', dest='numKochChars',
                        type=int, default=40,
                        help='Number of Koch Method characters to use')
    parser.add_argument('-w', '--words-min', action='store', dest='wpm', type=int,
                        default=20,
                        help='Character speed (words per minute) to generate')
    parser.add_argument('-n', '--farns-min', action='store', dest='farns', type=int,
                        default=5,
                        help='Farnsworth character speed to generate')

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

    

def main():
    args = parseArguments()

    progArgs = {}
    progArgs['numKochChars'] = args.numKochChars
    progArgs['farns'] = args.farns
    progArgs['wpm'] = args.wpm
    print(f"args: {progArgs}")

    charList = getKochChars(progArgs['numKochChars'])
    print(f"chars: {charList}")

    wordLst = getWordList(charList)
    print(f"words: {wordLst}")

    sys.exit(0)


if __name__ == '__main__':
    main()
