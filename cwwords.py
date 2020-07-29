#!/usr/bin/env python
# -*- mode: python -*-


import configargparse
import datetime
import gtts
import inspect
import os
import pydub
from pydub.playback import play
import random
import re
import string
import subprocess
import sys
import time



KOCH_CHARS = ['k', 'm', 'r', 's', 'u', 'a', 'p', 't', 'l', 'o',
              'w', 'i', '.', 'n', 'j', 'e', 'f', '0', 'y', 'v',
              ',', 'g', '5', '/', 'q', '9', 'z', 'h', '3', '8',
              'b', '?', '4', '2', '7', 'c', '1', 'd', '6', 'x']

CWOPS_CHARS = ['t', 'e', 'a', 'n', 'o', 'i', 's', '1', '4', 'r',
               'h', 'd', 'l', '2', '5', 'u', 'c', 'm', 'w', '3',
               '6', '?', 'f', 'y', 'p', 'g', '7', '9', '/', 'b',
               'v', 'k', 'j', '8', '0', 'x', 'q', 'z', '.', ',']

VOWELS = ['a', 'e', 'i', 'o', 'u', 'y']

PHONETIC_CHARS = [('A', 'alpha'), ('B', 'bravo'), ('C', 'charlie'), ('D', 'delta'),
                  ('E', 'echo'), ('F', 'foxtrot'), ('G', 'golf'), ('H', 'hello'),
                  ('I', 'india'), ('J', 'juliet'), ('K', 'kilo'), ('L', 'lima'),
                  ('M', 'mike'), ('N', 'november'), ('O', 'oscar'), ('P', 'papa'),
                  ('Q', 'quebec'), ('R', 'romeo'), ('S', 'sierra'), ('T', 'tango'),
                  ('U', 'uniform'), ('V', 'victor'), ('W', 'whiskey'),
                  ('X', 'xray'), ('Y', 'yankee'), ('Z', 'zulu')]

LOG_DATABASE_FILE = os.path.join(os.environ['HOME'], 'amateur-radio/log-database.db')

CW_INPUT_FILE =  "/tmp/ebook2cwinput.txt"

CW_OUTPUT_BASE = "cwoutput.mp3"
CW_OUTPUT_FILE = os.path.join("/tmp", CW_OUTPUT_BASE)

WORD_SND_BASE = "cwword-word-snd"
WORD_SND_FILE = os.path.join("/tmp", WORD_SND_BASE)

TONE_FILE = os.path.join(sys.path[0], "tone.mp3")

MY_CALLSIGN = "K6ZX"
MY_SKCC_NUM = 18552

QRZ_USERNAME   = 'K6ZX'
QRZ_PASSWORD   = 'Sean!12233'

MAX_QSO_LINES  = 6


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

    parser.add_argument('--words', action='store_true', dest='words',
                        help='Generate words')
    parser.add_argument('--callsigns', action='store_true', dest='callsigns',
                        help='Generate callsigns')
    parser.add_argument('--repeat-times', action='store', dest='repeat',
                        type=int, default = 1, help='Number of times to repeat word')
    parser.add_argument('--extra-wordspace', action='store', dest='extraWordSpace',
                        type=float, default = 0, help='Extra word spacing between words')
    parser.add_argument('-f', '--config-file', action='store', dest='configFile',
                        is_config_file=True, help='Config file path')
    parser.add_argument('--koch-chars', action='store', dest='numKochChars',
                        type=int, help='Number of Koch Method characters to use')
    parser.add_argument('--cwops-chars', action='store', dest='numCWOpsChars',
                        type=int, help='Number of CW Ops Method characters to use')
    parser.add_argument('--max-word-len', action='store', dest='maxWordLen',
                        type=int, default=256,
                        help='Minimum word length')
    parser.add_argument('--min-word-len', action='store', dest='minWordLen',
                        type=int, default=0,
                        help='Minimum word length')
    parser.add_argument('--wpm', action='store', dest='wpm', type=int,
                        default=20,
                        help='Character speed (words per minute) to generate')
    parser.add_argument('--farns-wpm', action='store', dest='farns', type=int,
                        default=5,
                        help='Farnsworth character speed to generate')
    parser.add_argument('--sound-file', action='store', dest='soundFilename',
                        type=str, default=CW_OUTPUT_FILE,
                        help='CW mp3 sound output file')
    parser.add_argument('--play', action='store_true', dest='play', default=False,
                        help='Play cw word file')
    parser.add_argument('--qsos', action='store_true', dest='qsos',
                        help='Generate QSOs')
    parser.add_argument('--rm-abbr', action='store_true', dest='rmAbbr',
                        default=False, help='Remove abbreviations from words')
    parser.add_argument('--total-words', action='store', dest='totalWords',
                        type=int, default=20,
                        help='Total number of words OR lines of QSO to output')
    parser.add_argument('--qso-line', action='store', dest='qsoLine',
                        type=str)
    parser.add_argument('--sidetone-freq', action='store', dest='freq',
                        type=int, default=600, help='Sidetone frequency (Hz)')
    parser.add_argument('--word-file', action='store', dest='wordFile', 
                        help='Word file path')
    parser.add_argument('--us-call-file', action='store', dest='usCallsignFile',
                        help='US callsign file path')
    parser.add_argument('--foreign-call-file', action='store', dest='foreignCallsignFile',
                        help='Foreign callsign file path')
    parser.add_argument('--ninja-mode', action='store_true', dest='ninjaMode',
                        help='Words generated in the Morse Ninja style')
    parser.add_argument('--ninja-cw-volume', action='store', dest='ninjaCwVolume',
                        default=0.2,
                        help='Ninja mode CW volume between 0 - 1')
    parser.add_argument('--ninja-call-phonetic', action='store_true',
                        dest='ninjaCallPhonetic',
                        help='Speak ninja callsigns phonetically')
    

    args = parser.parse_args()

    # print("-------------------------------------------------------------------")
    # print(parser.format_help())
    # print("-------------------------------------------------------------------")
    # print(parser.format_values())
    # print("-------------------------------------------------------------------")

    return args


def getKochChars(numChars):
    return KOCH_CHARS[:numChars]


def getCWOpsChars(numChars):
    return CWOPS_CHARS[:numChars]


def displayParameters(args, charList):
    if args['numKochChars'] is not None:
        text = f"Num Koch chars: {args['numKochChars']}\n"
    else:
        text = f"Num CWOPS chars: {args['numCWOpsChars']}\n"

    if args['numKochChars'] is not None and args['numKochChars'] < 40:
        print(f"Koch characters: {charList}")
    elif args['numCWOpsChars'] is not None and args['numCWOpsChars'] < 40:
        print(f"CW Ops characters: {charList}")
        
    if args['play']:
        text += (f"WPM: {args['wpm']}, Farns WPM: {args['farns']}, "
                 f"extra space: {args['extraWordSpace']} sec\n")
        if args['repeat'] is not None:
            text += f"repeat: {args['repeat']}, "

    print(text)

    
def getLOTWLogCallsigns():
    calllst = []
    logDbase = LogDatabase(LOG_DATABASE_FILE)          # init LogDatabase object
    dbCallLst = logDbase.doDBQuery("select call from callsigndata")

    for call in dbCallLst:
        # print(f"call: {call[0]}")
        calllst.append(call[0])

    return calllst

def getUSCallsigns(args):
    callLst = []

    with open(args['usCallsignFile'], 'r') as fileobj:
        for line in fileobj:
            elem = {}
            call = line.split('|')
            fileType = call[0]
            callsign = call[4]
            fullName = call[7]
            firstName = call[8]
            street = call[15]
            city = call[16]
            state = call[17]
            
            elem['fileType'] = fileType
            elem['callsign'] = callsign
            elem['fullName'] = fullName
            elem['firstName'] = firstName
            elem['street'] = street
            elem['city'] = city
            elem['state'] = state

            callLst.append(elem)
    
    return callLst


def getForeignCallsigns(args):
    callLst = []

    with open(args['foreignCallsignFile'], 'r') as fileobj:
        for line in fileobj:
            # print(f"line : {line}")
            elem = {}
            try:
                call = line.split('|')
                callsign = call[0]
                firstName = call[1]
                fullName = call[2]
                street = call[3]
                city = call[4]
                country = call[5]
            except IndexError as e:
                print(f"line: {line}")
                print(f"ERROR: {e}")
                sys.exit(1)

            elem['callsign'] = callsign
            elem['firstName'] = firstName
            elem['fullName'] = fullName
            elem['street'] = street
            elem['city'] = city
            elem['country'] = country
            # print(f"DEBUG: {elem}")
            
            callLst.append(elem)

    return callLst
            
    
def filterCallsigns(charList, calllst):
    # Remove callsigns that contain characters not in the character list
    tmpLst = []
    for call in calllst:
        for c in call:
            cl = c.lower()
            if cl not in charList:
                break
            else:
                pass
        else:
            tmpLst.append(call)

    return tmpLst



def getCallsignList(progArgs, charList):
    tmpLst = []

    usDataLst = getUSCallsigns(progArgs)
    usLst = []
    for x in usDataLst:
        usLst.append(x['callsign'])

    # print(f"DEBUG: {usLst}")
    print(f"Number of US callsigns: {len(usLst)}")

    usLst = filterCallsigns(charList, usLst)
    
    foreignDataLst = getForeignCallsigns(progArgs)
    foreignLst = []
    for x in foreignDataLst:
        foreignLst.append(x['callsign'])
        
    # print(f"DEBUG: {foreignDataLst}")
    print(f"Number of foreign callsigns: {len(foreignLst)}")

    foreignLst = filterCallsigns(charList, foreignLst)
    
    # temporarily return empty list for foreign list
    return usLst, foreignLst


def getWordList(progArgs, charList):
    wordLst = []

    # print(f"word file: {progArgs['wordFile']}")
    
    done = False
    with open(progArgs['wordFile'], 'r') as fileobj:

        for line in fileobj:
            line = line.strip()
            # print(f"line: {line}")

            # this allows there to be an explanation of some Q codes or
            # abbreviations in the file, delimited by '-'
            lst = line.split('-')
            # print(f"lst: {lst}")

            word = lst[0].strip()
            word = word.lower()
            # print(f"word: {word}")

            for c in word:
                # if (c not in charList) and (c.lower() not in charList):
                if c not in charList:
                    # print(f"c: {c}, word: {word}")
                    break
                else:
                    pass
            else:
                # print(f"append: {word}")
                wordLst.append(word)

    # debug
    # print(wordLst)
    # sys.exit(0)
    
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


def removeAbbreviations(progArgs, lst):
    if progArgs['rmAbbr']:
        wordLst = []
        for word in lst:
            # print(f"DEBUG word: {word}")
            for c in word:
                if c in VOWELS:
                    wordLst.append(word)
                    break
        return wordLst
    else:
        return lst


def generateCWSoundFile(progArgs, wordLst):
    words = ""

    # write word list to temporary file for input to 'ebook2cw' program
    with open(CW_INPUT_FILE, 'w') as fileobj:
        for word in wordLst:
            fileobj.write(f"{word}\n")

    for file in os.listdir('/tmp'):
        # print(f"file: {file}")
        if file.find(CW_OUTPUT_BASE) > -1 :
            absFile = os.path.join("/tmp", file)
            os.remove(absFile)
            # print(f"remove stale mp3 file: {absFile}")

    cmd = (f"/usr/bin/ebook2cw -w {progArgs['wpm']} -e {progArgs['farns']} "
           f"-W {progArgs['extraWordSpace']} -f {progArgs['freq']} "
           f"-o {progArgs['soundFilename']} "
           f"{CW_INPUT_FILE}")

    # proc = subprocess.run(cmd, shell=True, capture_output=True)
    proc = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode:
        print(f"ebook2cw return: {proc.returncode}")
    for line in proc.stdout.split('\n'):
        if re.search("^Total", line):
            print(line)


def convertToPhonetic(word):
    phoneticWord = ""

    for char in word:
        if char.isdigit():
            phoneticWord += (char + "  ")
        for elem in PHONETIC_CHARS:
            if elem[0] == char:
                phoneticWord += (elem[1] + "  ")

    return phoneticWord

    
# Ninja mode is based on the Morse Code Ninja website CW training
# method. It plays the CW for a word/phrase, then the word/phrase is
# spoken, and then the CW is played again. Then an alert tone is
# played to signal the next word/phrase sequence. 
def executeNinjaMode(progArgs, wordLst):
    # get the terminal width
    rows, columns = subprocess.check_output(['stty', 'size']).decode().split()
    columns = int(columns)         # convert to an integer
    numChars = 0
    print('')

    # alert tone to delineate word sequence
    tone = pydub.AudioSegment.from_mp3(TONE_FILE)
    # reduce volume of alert tone
    tone = tone - 12                  
    play(tone)

    print("")
    for word in wordLst:
        morseCmdLst = ['morse', f"-f {progArgs['freq']}", f"-v {progArgs['ninjaCwVolume']}",
                       f"-w {progArgs['farns']}", f"-F {progArgs['wpm']}"]
        # print(f"DEBUG: morseCmdLst = {morseCmdLst}")
        proc = subprocess.Popen(morseCmdLst, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            # print(f"DEBUG word: {word}")
            output, errors = proc.communicate(input=word.encode(), timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, errors = proc.communicate()
            print(f"ERROR: {errors}")

        time.sleep(1)

        if progArgs['ninjaCallPhonetic']:
            phonWords = convertToPhonetic(word)

        if progArgs['ninjaCallPhonetic']:
            # Right now, I like the Canadian voice in gTTS
            tts = gtts.gTTS(phonWords, lang='en-ca')
        else:
            tts = gtts.gTTS(word, lang='en-ca')
            
        tts.save(WORD_SND_FILE)
        wordSnd = pydub.AudioSegment.from_mp3(WORD_SND_FILE)
        play(wordSnd)

        proc = subprocess.Popen(morseCmdLst, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        try:
            output, errors = proc.communicate(input=word.encode(), timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, errors = proc.communicate()
            print(f"ERROR: {errors}")
        
        time.sleep(1)
    

        play(tone)
        time.sleep(1)
        numChars += len(word) + 1
        if numChars >= columns:
            endChar = '\n'
            numChars = 0
        else:
            endChar = ' '
        print(f"{word} ", end=endChar, flush=True)
        
    print('\n')


        
# remove duplicate words just for display purposes, no need to show the repeated
# words or callsigns.
def removeDuplicates(lst):
    finalLst = []
    for elem in lst:
        if elem not in finalLst:
            finalLst.append(elem)

    return finalLst
    

def playCWSoundFile(progArgs, wordLst):
    for file in os.listdir('/tmp'):
        if file.find(CW_OUTPUT_BASE) > -1:
            absFile = os.path.join("/tmp", file)
            cmd = f"/usr/bin/mpg123 {absFile}"
            # proc = subprocess.run(cmd, shell=True)
            proc = subprocess.run(cmd, shell=True, encoding='utf-8',
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
            if proc.returncode:
                print(f"mpg123 return: {proc.returncode}")



def displayGeneratedText(progArgs, wordLst):
    # get the terminal width
    rows, columns = subprocess.check_output(['stty', 'size']).decode().split()
    columns = int(columns)

    if progArgs['words']:
        print("\nWords Generated:")
    else:
        print("\nCallsigns Generated:")
        
    print("---------------------------------------------------------")
    numChars = 0
    # for word in removeDuplicates(wordLst):
    rwordLst = removeDuplicates(wordLst)
    for index, word in enumerate(rwordLst):
        # print(f"word list: {index}  {word}")
        if progArgs['qsos']:
            endChar = "\n"
        else:
            endChar = " "
        
        if word == 'vvvv':
            pass
        else:
            if progArgs['words']:
                numChars += len(word) + 1
            else:
                numChars += 6 + 1
                
            numNextChars = numChars + len(rwordLst[index])
                                 
            if numNextChars >= columns:       # print a newline if more chars than
                endChar = '\n'                # terminal width
                numChars = 0

            if progArgs['words']:
                print(f"{word}", end=endChar)
            else:
                print(f"{word:6s}", end=endChar)

    print("")
    print("---------------------------------------------------------")

    numChars = 0
    for word in wordLst:
        if word != 'vvvv':
            numChars += len(word)

    print(f"total characters: {numChars}")
    
    

def generateCallsigns(progArgs, charList):
    print('Generating callsigns...')
    usLst, foreignLst = getCallsignList(progArgs, charList)
    # print(f"num FCC calls: {len(usLst)}, "
    #       f"num foreign calls: {len(foreignLst)}")

    rnum = random.randint(60, 101) / 100
    fccnum = int(round(progArgs['totalWords'] * rnum))
    fornum = progArgs['totalWords'] - fccnum
    print(f"US calls: {fccnum}, foreign calls: {fornum}")

    if usLst:
        random.shuffle(usLst)
        trunFccLst = usLst[:progArgs['totalWords']]

        if foreignLst:
            trunFccLst = trunFccLst[:fccnum]

            random.shuffle(foreignLst)
            trunForeignLst = foreignLst[:fornum]

            callsignLst = trunFccLst + trunForeignLst
            
            random.shuffle(callsignLst)
        else:
            callsignLst = trunFccLst

        finalCallsignLst = []
        # if repeat is selected, repeat the words
        if progArgs['repeat']:
            repeatLst = []
            for element in callsignLst:
                for i in range(progArgs['repeat']):
                    repeatLst.append(element)

            finalCallsignLst = repeatLst

        if progArgs['ninjaMode']:
            executeNinjaMode(progArgs, finalCallsignLst)
        elif progArgs['play']:
            # Add 'vvvv' to beginning of list
            finalCallsignLst.insert(0, 'vvvv')
            generateCWSoundFile(progArgs, finalCallsignLst)
            
            time.sleep(2)
            playCWSoundFile(progArgs, finalCallsignLst)
        else:
            pass

        if not progArgs['ninjaMode']:
            displayGeneratedText(progArgs, finalCallsignLst)
    else:
        print("No callsigns were found using the input parameters, ")
        print("increase number of characters in set.")



def generateWords(progArgs, charList):
    # print('Generating words...')
    wordLst = getWordList(progArgs, charList)
    # print(f"word list: {wordLst}")
    wordLst = applyMinMax(progArgs, wordLst)
    # print(f"word list: {wordLst}")
    # wordLst = removeAbbreviations(progArgs, wordLst)

    if wordLst:
        random.shuffle(wordLst)
        trunWordLst = wordLst[:progArgs['totalWords']]
        # print(f"num words: {len(trunWordLst)}")
        # print(f"\n\nwords: {trunWordLst}")

        if progArgs['ninjaMode']:
            executeNinjaMode(progArgs, trunWordLst)

        elif progArgs['play']:
            # print('DEBUG: playing CW...')
            # Add 'vvvv' to beginning of list
            trunWordLst.insert(0, 'vvvv')
            generateCWSoundFile(progArgs, trunWordLst)
            
            time.sleep(2)
            playCWSoundFile(progArgs, trunWordLst)
        else:
            pass

        if not progArgs['ninjaMode']:
            displayGeneratedText(progArgs, trunWordLst)
    else:
        print("No words were found using the input parameters, decrease word length")
        print("and/or increase number of characters in set.")


def generateSkccNum():
    rnum = random.randint(1, 25000)
    return rnum
    
def generateQSOs(progArgs, charList):
    print('Generating QSOs...')
    callLst = getLOTWLogCallsigns()
    print(f"num LOTW calls: {len(callLst)}")
    random.shuffle(callLst)
    dxStation = callLst[0]

    rnum = random.randint(0, 100)
    # if rnum > 50:
    if rnum > 100:      # modify so call is always TO me, not FROM me
        dxStation = callLst[0]
        deStation = MY_CALLSIGN
    else:
        dxStation = MY_CALLSIGN
        deStation = callLst[0]

    dxCall = f"{dxStation} DE {deStation}"
    deCall = f"{deStation} DE {dxStation}"

    qrz = QRZ(QRZ_USERNAME, QRZ_PASSWORD)
    dxCallData = qrz.callsignData(dxStation, verbose=False)
    dxOP = dxCallData['fname'].split(' ')[0]
    dxCity = dxCallData['addr2']
    if 'state' in dxCallData:
        dxLoc = dxCallData['state']
    else:
        dxLoc = dxCallData['country']

    deCallData = qrz.callsignData(deStation, verbose=False)
    deOP = deCallData['fname'].split(' ')[0]
    deCity = deCallData['addr2']
    if 'state' in deCallData:
        deLoc = deCallData['state']
    else:
        deLoc = deCallData['country']

    if deStation == MY_CALLSIGN:
        deSKCCNum = MY_SKCC_NUM
        dxSKCCNum = generateSkccNum()
    else:
        deSKCCNum = generateSkccNum()
        dxSKCCNum = MY_SKCC_NUM

    now = datetime.datetime.now()
    if 3 <= now.hour < 12:
        salutation = "GM"
    elif 12 <= now.hour < 20:
        salutation = "GE"
    else:
        salutation = "GN"

    deRead = random.randint(1, 5)
    deStrgth = random.randint(1, 9)
    deTone = random.randint(1, 9)
    dxRead = random.randint(1, 5)
    dxStrgth = random.randint(1, 9)
    dxTone = random.randint(1, 9)

    qsoLst = ['vvvv']
    qsoLine = []

    print(f"DEBUG qsoline: {progArgs['qsoLine']}")
    if progArgs['qsoLine'] == None:
        qsoLine = [1, 2, 3, 4, 5, 6]
    else:
        for item in progArgs['qsoLine'].split(','):
            qsoLine.append(int(item))
    
    if qsoLine == []:
        qsoLine = [1, 2, 3, 4, 5, 6]

    # use a random number to decide on number of CQs
    if 1 in qsoLine:
        if dxRead < 2:
            qsoLst.append(f"CQ CQ CQ DE {deStation} {deStation} {deStation} K")

        else:
            qsoLst.append(f"CQ CQ DE {deStation} {deStation} K")

    #    if qsoLine == MAX_QSO_LINES or qsoLine == 2:
    if 2 in qsoLine:
        if dxRead < 2:
            qsoLst.append(f"{deStation} {deStation} DE "
                          f"{dxStation} {dxStation} <AR>")
        else:
            qsoLst.append(f"{deStation} DE "
                          f"{dxStation} {dxStation} <AR>")
            
    if 3 in qsoLine:
        call      = f"{dxStation} DE {deStation}"
        greeting  = f"TNX FER CALL <BT>"
        signalRpt = f"UR RST {dxRead}{dxStrgth}{dxTone} {dxRead}{dxStrgth}{dxTone} <BT>"
        qthRpt    = f"HR QTH {deCity} {deLoc} {deCity} {deLoc} <BT>"
        nameRpt   = f"NAME {deOP} {deOP} SKCC {deSKCCNum} {deSKCCNum} HW? <BK>"
        qsoLst.append(f"{greeting} {signalRpt} {qthRpt} {nameRpt}")

    if 4 in qsoLine:
        call      = f"{deStation} DE {dxStation}"
        greeting  = f"R R {salutation} ES TNX FER CALL <BT>"
        signalRpt = f"UR RST {dxRead}{dxStrgth}{dxTone} {dxRead}{dxStrgth}{dxTone} <BT>"
        qthRpt    = f"HR QTH {deCity} {deLoc} {deCity} {deLoc} <BT>"
        nameRpt   = f"NAME {deOP} {deOP} SKCC {deSKCCNum} {deSKCCNum} HW? <BK>"
        qsoLst.append(f"{greeting} {signalRpt} {qthRpt} {nameRpt}")

    if 5 in qsoLine:
        call      = f"{dxStation} DE {deStation}"
        greeting  = f"TNX FER FB QSO {dxOP} <BT> HP CU AGN 73 <SK>"
        qsoLst.append(f"{greeting} {call} i")

    if 6 in qsoLine:
        call      = f"{deStation} DE {dxStation}"
        greeting  = f"TNX FER QSO {deOP} <BT> 73 <SK>"
        qsoLst.append(f"{greeting} DE {call} i")

    # print(f"DEBUG  qsoLst: {qsoLst}")

    generateCWSoundFile(progArgs, qsoLst)
    
    if progArgs['play']:
        time.sleep(2)
        playCWSoundFile(progArgs, qsoLst)
    else:
        pass

    displayGeneratedText(progArgs, qsoLst)

    # print()
    # for line in qsoLst:
    #     print(line)
        
    

def main():
    args = parseArguments()

    progArgs = {}
    progArgs['callsigns'] = args.callsigns
    progArgs['repeat'] = args.repeat
    progArgs['numKochChars'] = args.numKochChars
    progArgs['numCWOpsChars'] = args.numCWOpsChars
    progArgs['farns'] = args.farns
    progArgs['wpm'] = args.wpm
    progArgs['extraWordSpace'] = args.extraWordSpace
    progArgs['freq'] = args.freq
    progArgs['totalWords'] = args.totalWords
    progArgs['qsoLine'] = args.qsoLine
    progArgs['rmAbbr'] = args.rmAbbr
    progArgs['soundFilename'] = args.soundFilename
    progArgs['play'] = args.play
    progArgs['maxWordLen'] = args.maxWordLen
    progArgs['minWordLen'] = args.minWordLen
    progArgs['words'] = args.words
    progArgs['qsos'] = args.qsos
    progArgs['ninjaMode'] = args.ninjaMode
    progArgs['ninjaCwVolume'] = args.ninjaCwVolume
    progArgs['ninjaCallPhonetic'] = args.ninjaCallPhonetic
    if args.wordFile:
        progArgs['wordFile'] = os.path.abspath(args.wordFile)
    if args.usCallsignFile:
        progArgs['usCallsignFile'] = os.path.abspath(args.usCallsignFile)
    if args.foreignCallsignFile:
        progArgs['foreignCallsignFile'] = os.path.abspath(args.foreignCallsignFile)
    # if args.commonFile:
    #     progArgs['commonFile'] = os.path.abspath(args.commonFile)
        
    # print(f"args: {progArgs}")

    if progArgs['numKochChars'] is not None:
        charList = getKochChars(progArgs['numKochChars'])
        # print(f"Koch characters: {charList}")
        # print(f"Number of Koch characters: {progArgs['numKochChars']}\n")
    elif progArgs['numCWOpsChars'] is not None:
        charList = getCWOpsChars(progArgs['numCWOpsChars'])
        # print(f"CW Ops characters: {charList}")
        # print(f"Number of CW Ops characters: {progArgs['numCWOpsChars']}\n")

    displayParameters(progArgs, charList)
    
    if progArgs['callsigns']:
        generateCallsigns(progArgs, charList)
    elif progArgs['words']:
        generateWords(progArgs, charList)
    # else:
    #     generateQSOs(progArgs, charList)

    sys.exit(0)


if __name__ == '__main__':
    main()
