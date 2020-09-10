# Morse Code Training Utility: cwwords

The **cwwords** package provides several training modes to assist in
CW training.


## Table of Contents

* [General Info](#general_info)
* [Word Generation](#word_generation)
* [Callsign Generation](#callsign_generation)
* [Ninja Mode](#ninja_mode)
* [Installation](#installation)
* [Invocation](#invocation)

<a name="general_info"></a>
## General Info

The **cwwords** package is a Morse Code practice application that has
several different modes for CW training. These modes are: *word*
generation, *callsign* generation, and *ninja* mode. In these modes
words or callsigns are generated randomly and then the resulting CW is
played. For all of these modes there are parameters that can be set to
control the training mode, the character set to use and the details of
the Morse Code that is generated and played. Training with words or
callsigns can be more satisfying than copying random characters. The
*ninja* mode is a new revolutionary training methodology.

<a name="word_generation"></a>
## Word Generation

The *word* generation mode generates a number of random words for which
the CW is played. There is also an option to generate a list of words
without playing the CW. The character set that is used to generate
words can be limited to a subset of the Morse characters so that word
training can be done before the entire character set has been
learned. This capability allows earlier access to more advanced and
interesting training. There are two different character 'orders' that
are implemented, the Koch character order and the CWOps/CW Academy
training order, so that words or callsigns can be generated using the
subset of the character set that one has learned. The minimum and
maximum length of the words may be also set allowing shorter words to
be trained initially, then progressing to longer words.

The CW that is played may also be controlled by allowing the setting of
the tone frequency, character speed, Farnsworth speed, additional word
spacing, and number of times to repeat each word.

<a name="callsign_generation"></a>
## Callsign Generation

The *callsign* generation mode generates a number of actual callsigns,
both U.S. and international callsigns, randomly selected. The CW for
these callsigns is either played or a list of the callsigns is
displayed instead of being played. As in the word generation mode, the
character set that is used to generate the callsigns can be limited to
a subset of the Morse characters so that callsign training can be done
before the entire character set has been learned. There are two
different training *orders* that are implemented, the Koch character
order and the CWOps/CW Academy training order so that callsigns can be
generated using the subset of the character set that one has learned.

As in the word generation mode, the CW that is played may also be
controlled by allowing the setting of the tone frequency, character
speed, Farnsworth speed, additional word spacing, and number of times
to repeat each callsign.

<a name="ninja_mode"></a>
## Ninja Mode

*Ninja* mode implements a unique training methodology pioneered by
Kurt Zoglmann, AD0WE, and introduced on his website
<https://morseninja.info>. In this mode, an alert tone is played to
signify the start of a *word sequence*. The *word sequence* consists
of playing the CW for the word or callsign, allowing the trainee to
headcopy what is sent, then the word or callsign is spoken by the
program, and then the CW is played again. The theory is that learning
is enhanced through listening to CW that is sent, hearing the correct
word or callsign spoken to reinforce what was sent, and then hearing
an immediate repeat of the CW. See Kurt's website for more details of
this training method.

<a name="installation"></a>
## Installation

The **cwwords** package is implemented in Python and requires
python 3. It can be executed from source code in the manner of any
python script, but the easiest method of deployment and execution is
to use the **cwwordsapp** package that is the single file executable
for all supported operating systems. The **cwwordsapp** is packaged
separately and should be accessed from that repository.

For those knowledgeable/interested users, **cwwords** may be executed
from source as follows. It is developed/tested on a Linux OS using the
Python Version Management Tool,
[pyenv](https://github.com/pyenv/pyenv), and creating a python
[virtual environment](https://docs.python.org/3/library/venv.html)
(i.e. python -m venv venv). The python interpreter and required python
modules are installed in the local virtual environment. In this way
the entire required python support system is available locally. The
required python modules are identified in the file 'requirements.txt'
and are installed in the local virtual environment using:

    *pip install -r requirements.txt*

The **cwwords** package runs in a terminal session and is invoked from
the command line. its operation is configured with either a
configuration file or optional command line arguments. While either
way is effective, using a configuration file is probably the easiest
method of use. A set of default configuration files can be written
using:

   cwwords.py --init <config_dir>
   
 where *config_dir* is a directory in which the program's
 configuration files is stored. 
 
 The **cwwords** package is invoked as follows:
 
``` 
 usage: cwwords.py [-h] [--init CONFIGDIR] [--words] [--callsigns] [--repeat-times REPEAT]
                  [--extra-wordspace EXTRAWORDSPACE] [-f CONFIGFILE] [--koch-chars NUMKOCHCHARS]
                  [--cwops-chars NUMCWOPSCHARS] [--max-word-len MAXWORDLEN]
                  [--min-word-len MINWORDLEN] [--wpm WPM] [--farns-wpm FARNS] [--noise NOISESNR]
                  [--sound-file SOUNDFILENAME] [--play] [--qsos] [--rm-abbr]
                  [--total-words TOTALWORDS] [--qso-line QSOLINE] [--sidetone-freq FREQ]
                  [--word-file WORDFILE] [--ninja-mode] [--ninja-cw-volume NINJACWVOLUME]
                  [--ninja-call-phonetic]

CW Words audio file generator. Args that start with '--' (eg. --init) can also be set in a config file (specified via -f). Config file syntax allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at https://goo.gl/R74nmi). If an arg is specified in more than one place, then commandline values override config file values which override defaults.

optional arguments:
  -h, --help            show this help message and exit
  --init CONFIGDIR      Initialize cwwords.py configuration files into directory (default: None)
  --words               Generate words (default: False)
  --callsigns           Generate callsigns (default: False)
  --repeat-times REPEAT
                        Number of times to repeat word (default: 1)
  --extra-wordspace EXTRAWORDSPACE
                        Extra word spacing between words (default: 0)
  -f CONFIGFILE, --config-file CONFIGFILE
                        Config file path (default: None)
  --koch-chars NUMKOCHCHARS
                        Number of Koch Method characters to use (default: None)
  --cwops-chars NUMCWOPSCHARS
                        Number of CW Ops Method characters to use (default: None)
  --max-word-len MAXWORDLEN
                        Minimum word length (default: 256)
  --min-word-len MINWORDLEN
                        Minimum word length (default: 0)
  --wpm WPM             Character speed (words per minute) to generate (default: 20)
  --farns-wpm FARNS     Farnsworth character speed to generate (default: 5)
  --noise NOISESNR      Add background noise with SNR (default: 0)
  --sound-file SOUNDFILENAME
                        CW mp3 sound output file (default: /tmp/cwwords)
  --play                Play cw word file (default: False)
  --qsos                Generate QSOs (default: False)
  --rm-abbr             Remove abbreviations from words (default: False)
  --total-words TOTALWORDS
                        Total number of words OR lines of QSO to output (default: 20)
  --qso-line QSOLINE
  --sidetone-freq FREQ  Sidetone frequency (Hz) (default: 600)
  --word-file WORDFILE  Word file path (default: None)
  --ninja-mode          Words generated in the Morse Ninja style (default: False)
  --ninja-cw-volume NINJACWVOLUME
                        Ninja mode CW volume between 0 - 1 (default: 0.2)
  --ninja-call-phonetic
                        Speak ninja callsigns phonetically (default: False)

'cwwords' is a Morse Code practice application that has several 
different modes to assist in CW training. There are three fundamental 
modes used for training: word generation, callsign generation, and 
'ninja' mode. For all of these modes there are parameters that can be 
set to control the character set to use and the details of the Morse 
Code that is generated.

The character set to use for the word or callsign generation can be 
set. This is intended for training when the full 40 characters have 
not yet been learned, but enough have been learned to start useful 
training with words and callsigns. There are two different character 
training 'orders', the Koch character order and the CW Academy 
character order. The number of characters in one of these orders is 
identified and then words or callsigns that are generated are limited 
to these characters. Details of the the words generated may also be 
set: word length: to allow shorter words to be trained initially then 
progressing to longer words and number of words in each session.

Additionally the details of the Morse Code that is generated 
can be specified with the usual parameters: tone frequency, character
speed, farnsworth speec, additional word spacing, number of times to 
repeat each word. 

There are three basic modes of operation: word generation, callsign
generation, and 'ninja' mode.
 
Word generation mode generates words, filtered according to the settings 
to the mode (e.g. word length, character set) and then the Morse Code 
for the words is played.

Callsign generation mode performs a similar function to word generation, 
except that callsigns (both U.S. and International) are generated.

'Ninja' mode is a mode that follows the unique teaching method pioneered 
(as far as I know) by Kurt Zoglmann, AD0WE and made popular on his website,
<https://morsecode.ninja>. In this mode, an alert tone is played to signify
the start of a word sequence. The word sequence consists of the Morse Code 
for a word, followed by the spoken word, followed by the Morse Code for the
word again. This sequence repeats for the number of words that has been 
configured. As in the other modes, the details of the character set, word 
filtering, and code speed can all be specified.

```

