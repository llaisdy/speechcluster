# SpeechCluster: A speech database builder's multitool
## Overview

SpeechCluster is on [PyPi](https://pypi.org/project/speechcluster/), and can be installed with

```
$ pip install speechcluster
```

### Introduction

SpeechCluster is a library, and a cli (`sc`) for working with speech data, in the form of sound files and their associated transcriptions.  The primary use case (at least, what I use it for) is for building acoustic models.

I created the first version in the early years of the 21st century, working on Welsh speech data at the University of Wales Bangor.  I am now bringing it up to date, preparatory to hooking it up with PyTorch and others.

If you use SpeechCluster or its associated tools in published research, please let me know!  And please use this citation in your references section: 

> Uemlianin, I. A.  (2005).  *SpeechCluster: A speech database builder's multitool*.  Lesser Used Languages & Computer Linguistics proceedings. European Academy, Bozen/Bolzano, Italy.

### Requirements

SpeechCluster and the associated command-line tools are all written in Python & tested with Python 3.12.  Most Linux distrubutions come with Python as standard.  If Python is not installed on your system, it is very simple to install (especially on Windows and MacOS X systems).  The Python home page is here:  <http://www.python.org>.

`sc dibo` ("diphone boundaries", see below) uses a couple of commands from the [Edinburgh Speech Tools library](https://www.cstr.ed.ac.uk/projects/speech_tools/), namely `ch_wave` and `pitchmark`.  In order to use `dibo`, these two commands should be on your `PATH`.  NB: `dibo` is currently deprecated while I either fix some bugs or remove it altogether.  If you'd like to use this subcommand, please get in touch.

At the moment, the only audio format supported by SpeechCluster is Microsoft's RIFF format (.wav).  Furthermore, SpeechCluster assumes audio signals are mono.  For this reason, the unix utility `sox` will be useful.  Linux distributions will have this.  The `sox` homepage is: <http://sox.sourceforge.net>.

### Local Installation

As well as downloading from pypi, speechCluster.py and all the command-line tools below are in the speechcluster directory in this repo.  The cli can be accessed via `python -m speechcluster` or, better, by installing locally with [build](https://pypi.org/project/build/), as in:

```
$ pip install -r requirements-packaging.txt
$ python -m build
...
Successfully built speechcluster-2.0.0.tar.gz and speechcluster-2.0.0-py3-none-any.whl
$ l dist/
speechcluster-2.0.0-py3-none-any.whl
speechcluster-2.0.0.tar.gz
$ mkdir install.d
$ mv dist/ install.d/
$ mv speechcluster.egg-info/ install.d/
$ pip install install.d/dist/speechcluster-2.0.0-py3-none-any.whl
...
Successfully installed speechcluster-2.0.0
```

### Development Roadmap

Some proximate goals for SpeechCluster are:

- improve test coverage and code quality
- add `sc force` subcommand to do forced alignment with PyTorch
- expand remit to include
  - corpus management
  - more general frontend to PyTorch/JAX/etc

## `sc` and its subcommands
### Overview

These subcommands can be used as they are, or they can be taken as example use-cases for SpeechCluster.  If none of these tools fits your exact requirements, you may be able to change the code of the nearest fit, or even to write your own subcommand (or submit a feature request!).

The `sc` help message lists the available subcommands:

```
$ sc -h

usage: sc [-h] {fake,inter,merge,replace,switch,splitall,trim} ...

options:
  -h, --help            show this help message and exit

subcommands:
  {fake,inter,merge,replace,switch,splitall,trim}
                        SpeechCluster operations
    fake                Fake segmentation
    inter               Interpolate labels
    merge               Merge tiers
    replace             Replace selected symbols in a tier
    switch              Convert between label file formats
    splitall            Split all files in directory
    trim                Trim beginning and end silence from wav files
```

And the help message for each subcommand shows information about arguments:

```
$ sc fake -h
usage: sc fake [-h] (-d DIRECTORY | -f FILE) -o
               {esps,htkgrm,htklab,htkmlf,lab,seg,TextGrid} [-c CONTEXT]
               [labels ...]

positional arguments:
  labels                labels to add

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        directory for input
  -f FILE, --file FILE  input file
  -o {esps,htkgrm,htklab,htkmlf,lab,seg,TextGrid}, --outFormat {esps,htkgrm,htklab,htkmlf,lab,seg,TextGrid}
                        output format
  -c CONTEXT, --context CONTEXT
                        json file with transDict
```

nb: the sections below use the new `sc <subcommand>` form, but the original scripts are still functional, and the old "user interface" will still work.  As an example, the first section gives examples for both.

### `sc fake` (segFake.py)

`sc fake` does "fake autosegmentation" of a speech audio file.  At the moment it assumes one utterance per file, with bounding silences.  segFake detects utterance onset and offset, and spreads the given labels evenly over the intervening time.

The chances of getting any label boundary correct are of course virtually zero, but I have found it quicker and easier to correct one of these than to start labelling from scratch.  Correcting a "fake" transcription is also less error-prone, as the labels to use are already provided and don't need to be specified by the user.

#### Usage

Fake segment a single audio file, output label file of the specified format, using the labels given inline:

    sc fake -f <filename> -o (TextGrid | esps | htklab ) <phones>
    segFake.py -f <filename> -o (TextGrid | esps | htklab ) <phones>
    
    # e.g.:
    sc fake -f amser012.wav -o TextGrid  m ai hh ii n y n j o n b y m m y n y d w e d i yy n y b o r e

Fake segment all audio files in the given directory, using the specified transcription file:

    sc fake -d <dirname> -c <context filename> -o (TextGrid | esps | htklab)
    segFake.py fake -d <dirname> -c <context filename> -o (TextGrid | esps | htklab)
    
    # e.g.:
    sc fake -d wav -c context.json -o TextGrid 

The context json file should contain a "transDict" object, where keys are filename stems (ie no extension) and values are transcriptions, eg:

    {
     ...
        "transDict": {
            "common_voice_en_34926907": "I'm sending you on a dangerous mission",
            "common_voice_en_35387333": "noone else could claim that",
            "common_voice_en_36528488": "he was never identified or captured"
        }
    }

### `sc inter` (segInter.py)

`sc inter` interpolates labels into a segmented but unlabelled segment tier.  For example, you label a file phonemically, mark the word boundaries but don't type in the words themselves.  If you have the text available, you can use segInter to fill in the word tier.  This can save you a lot of typing and fiddling about.

#### Usage

Add word labels into a file:

    sc inter [-l <level>] -f <label filename> <labels>
    
    # e.g.:
    sc inter -f amser035.TextGrid Mae hi ychydig wedi chwarter i hanner nos

Add word labels into all files in a directory, using the given transcription file:

    sc inter [-l <level>] -d <dir> -c <context filename>
    
    # e.g.:
    segInter -d lab -c context.json

#### Notes

-   only TextGrid label format is supported
-   the default level/tierName is "Word"
-   labels do not have to be quoted on the command-line
-   see `fake` for transcription file format.
-   `inter` assumes that the first and last segments in the textGrid are silence, and adds Word-level silences accordingly (i.e. don't specify them explicitly).

### `sc merge` (segMerge.py)

Merges label files into one multi-tiered label file, for example to compare different segmentations of a speech file.

n.b.: Currently only works on textGrids (and takes first tier of multi-tiered textGrids).

#### Usage

    sc merge <fn1> <tierName> <fn2> <tierName> <fn3> <tierName> ...
    
    # e.g.:
    sc merge eg1.TextGrid Me eg2.TextGrid Them eg2.TextGrid Fake ...

### `sc replace` (segReplace.py)

Label file label converter.

n.b.: `replace` changes labels in place, so keep a back-up of your old versions!

#### Usage

    sc replace -c <context filename> <segfilename>
    sc replace -c <context filename> -d <dirname>

The context json file should contain a "replaceDict" object where keys are old labels (to replace) and values are labels to replace them, eg:

    {
        ...
        "replaceDict": {"aa": "!!merge",
                        "t sh": "ch",
                        "@": "ax"}
    }

n.b.:

-   Quote marks are required;
-   If an old label has `!!merge` as its new label, segments with that label are merged with the previous segment (i.e., the segment is removed, and the previous label's end time is extended).
-   old labels can be longer than a single label.  Currently they can be no longer than two labels.

### `sc switch` (segSwitch.py)

`sc switch` converts between label file formats, either on single files, or a directory at a time.

#### Usage

    sc switch -i <infilename> -o <outfilename>
    sc switch -i <infilestem>.mlf -o <outFormat>
    sc switch -d <dirname> -o <outFormat>

Formats supported:

| Format                | File Extension(s) |
|-----------------------|-------------------|
| esps                  | .esps, .lab, .seg |
| Praat TextGrid        | .TextGrid         |
| htk label file        | .htk-lab          |
| htk master label file | .htk-mlf          |
| htk transcription     | .htk-grm          |


n.b.: currently, `switch` will only convert **into** not **out of** htk-grm format.

### `sc splitall` (splitAll.py)

`sc splitall` takes a directory full of paired speech audio and label files (e.g., wav and TextGrid), and splits each audio/labelfile pair into paired subsections, according to various split parameters such as number of units or silence (where "units" can be phones, words, silences, etc.).

#### Usage

    sc splitall -n <integer> -t <tierName> [-l <label>] inDir outDir

inDir should contain pairs of speech audio and label files (e.g., wav and TextGrid).  splitAll will split each pair into shorter paired segments, based on the parameters given.

#### Examples

    sc splitall -n 5 -t Phone in/ out/         # into 5 phone chunks
    
    sc splitall -n 1 -t Word in/ out/          # by each word
    
    sc splitall -n 1 -t Phone -l sil in/ out/  # by each silence
    
    sc splitall -n 5 -t Second in/ out/        # into 5 sec chunks

### [`sc dibo` (segDiBo.py)]

- **WARNING: this subcommand is possibly unreliable, is deprecated, and may be removed soon**

`sc dibo` adds explicit diphone boundaries to label files, ready for use in festival diphone synthesis.  It also outputs pitchmark (pm) files.  segDiBo'd label files (`fstem_dibo.ext`) and pm files are output into the given data directory.

The input directory should contain paired wav and TextGrid files.

#### Usage

    sc dibo -d <dataDirectory>

### `sc trim` (trim.py)

Trims beginning and end silence from wav files, adjusts any associated label files accordingly.

#### Usage

    sc trim -p 1.5 example.wav  # trims example.wav leaving 1.5s padding
    sc trim -p 1.5 example  # as above, adjusts any seg files found too 
    
    sc trim -d testdir  # trims all files in testdir, including any seg files,
                        # leaving .5s padding

## SpeechCluster.py

SpeechCluster.py is a python module containing some object classes - Segment, SegmentationTier and SpeechCluster - which represent speech segmentation and the associated audio.  SpeechCluster can read and write a number of label file formats, and wav format audio.

Supported Label formats include:

| Format    | As used by                       | SpeechCluster name |
|-----------|----------------------------------|--------------------|
| .TextGrid | Praat                            | TextGrid           |
| .lab      | Emu, Festival                    | lab, esps          |
| .lab      | HTK (n.b.: different from above) | htk-lab            |
| .mlf      | HTK                              | htk-mlf            |
| .txt      | HTK                              | htk-grm            |

SpeechCluster can read/write/convert any of these formats in any direction.

## Acknowledgements

This work was carried out as part of the project "Welsh and Irish Speech Processing Resources" (Prys, et al., 2004).  WISPR was funded by the Interreg IIIA European Union Programme and the Welsh Language Board. I should also like to acknowledge support and feedback from other members of the WISPR team, in particular Briony Williams and Aine Ni Bhrian.

The three audio files in `test/data/` are taken from Mozilla's [Common Voice](https://commonvoice.mozilla.org) corpus for English.

## References

Prys, Delyth, Briony Williams, Bill Hicks, Dewi Jones, Ailbhe Ní Chasaide, Christer Gobl, Julie Berndsen, Fred Cummins, Máire Ní Chiosáin, John McKenna, Rónán Scaife, Elaine Uí Dhonnchadha.  (2004).  *WISPR: Speech Processing Resources for Welsh and Irish*.  Pre-Conference Workshop on First Steps for Language Documentation of Minority Languages, 4th Language Resources and Evaluation Conference (LREC), Lisbon, Portugal, 24-30 May 2004.

Uemlianin, Ivan A.  (2005).  *SpeechCluster: A speech database builder's multitool*.  Lesser Used Languages & Computer Linguistics proceedings. European Academy, Bozen/Bolzano, Italy.
