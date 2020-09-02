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
played. For all of these modes that are parameters that can be set to
control the character set to use and the details of the Morse Code
that is generated and played. Training with words or callsigns can be
more satisfying than copying random characters and *ninja* mode is
thought to be a revolutionary training methodology .

<a name="word_generation"></a>
## Word Generation

The *word* generation mode generates a number of random words for which
the CW is played. There is also an option to generate a list of words
without playing the CW. The character set that is used to generate
words can be limited to a subset of the Morse characters so that word
training can be done before the entire character set has been
learned. This capability allows earlier access to more advanced and
interesting training. There are two different training 'orders' that
are implemented, the Koch character order and the CWOps/CW Academy
training order so that words or callsigns can be generated using the
subset of the character set that one has learned. The minimum and
maximum length of the words may be also set allowing shorter words to
be trained initially, then progressing to longer words.

The CW that is played may also be controlled with the following
parameters: tone frequency, character speed, Farnsworth speed,
additional word spacing, and number of times to repeat each word. 

<a name="callsign_generation"></a>
## Callsign Generation

The *callsign* generation mode generates a number of actual callsigns,
both U.S. and international, randomly selected. The CW for these
callsigns is either played or a list of the callsigns is displayed
instead of being played. As in the word generation mode, the character
set that is used to generate the callsigns can be limited to a subset
of the Morse characters so that callsign training can be done before
the entire character set has been learned. This capability allows
earlier access to more advanced and interesting training. There are
two different training *orders* that are implemented, the Koch
character order and the CWOps/CW Academy training order so that
callsigns can be generated using the subset of the character set that
one has learned.

As in the word generation mode, the CW that is played may also be
controlled with the following parameters: tone frequency, character
speed, Farnsworth speed, additional word spacing, and number of times
to repeat each word.

<a name="ninja_mode"></a>
## Ninja Mode

*Ninja* mode implements a unique training methodology pioneered (as
far as I know) by Kurt Zoglmann, AD0WE, and introduced on his website
<https://morseninja.info>. In this mode, an alert tone is played to
signify the start of a *word sequence*. The *word sequence* consists
of playing the CW for the word or callsign, allowing the trainee to
headcopy what is sent, then the word or callsign is spoken, and then
the CW is played again. The theory is that learning is enhanced
through listening to CW that is sent, hearing the correct word or
callsign spoken to reinforce what was sent, and then hearing an
immediate repeat of the CW. See Kurt's website for more details of
this training method.

<a name="installation"></a>
## Installation

The **cwwords** package is implemented in Python and requires
python 3. It has only been tested on a Linux OS so it is not known at
this time whether it will run on Mac OS or Windows(!). It has been
tested using the Python Version Management Tool, pyenv, and creating a
python virtual environment (i.e. python -m venv venv). The required
python modules are installed in the local virtual environment. The
required python modules are identified in the file 'requirements.txt'
in the common manner. Using the system python and installing the
necessary modules will almost certainly work also. There is a shell
script, **cwwords**, included in the package that can be installed in
the user's PATH to make executing **cwwords.py** easier, it will need
to be modified somewhat to account for the location in the user's
account that cwwords has been installed.

**cwwords** can perform initialization of its data files and
configuration files. This is done with the following invocation: 

  $ cwwords.py --init <config_dir>
  
  where <config_dir> is a directory in which the program's
  configuration files are stored. 
  
There are several default configuration files that are written to this
directory that contain the configuration parameters for each of the
modes of operation of **cwwords**. 


<a name="invocation"></a>
## Invocation

The **cwwords** package 

