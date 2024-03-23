#! /usr/bin/env python3

"""
* segInter: interpolates labels into an empty segmentation tier

** TODO

"""

import json

from .speechCluster import *
from .utils import set_directory

def segInter(fn, labList, level='Word'):
    seg = SpeechCluster(fn)
    tier = seg.getTierByName(level)
    labList = prepLabs(labList)
    for segment in tier:
        if segment.label == '':
            segment.label = labList.pop(0)
    with open(fn, 'w') as f:
        f.write(seg.write_format())


def segInterDir(dirn, transDict, level='Word'):
    items = list(transDict.items())
    with set_directory(dirn):
        for fstem, phonData in items:
            fn = f'{fstem}.TextGrid'
            labList = phonData.replace('.', '').replace('"', '').split()
            segInter(fn, labList, level)

def parsePromptFn(promptFn):
    items = []
    data = list(open(promptFn))
    for line in data:
        line = line[1:-2] # strip off brackets and newline
        ll = line.split()
        fn = '%s.TextGrid' % ll.pop(0) # only textgrids supported
        #labList = prepLabs(' '.join(ll))
        items.append((fn, ll))
    return items

def prepLabs(labs):
    labList = labs[:]
    if labList[0][0] in ['"', "'"]: # remove quotes
        labList[0] = labList[0][1:]
        labList[-1] = labList[-1][:-1]
    if labList[-1][-1] in ['.', '!', '?']:
        labList[-1] = labList[-1][:-1] # remove final punct
    labList.insert(0, 'sil')
    labList.append('sil')
    return labList

def printUsage():
    print("""segInter.py: Interpolates labels into label file

Usage:

  segInter.py [-l <level>] -f <label filename> <labels>

    e.g.: segInter.py -f amser035.TextGrid Mae hi ychydig wedi chwarter i hanner nos

  segInter.py [-l <level>] -d <dir> -i <prompt filename>

    e.g.: segInter.py -d lab -i amser.data

#### silence or no silence? ####


Notes:

- only TextGrid label format is supported
- the default level/tierName is 'Word'
- labels do not have to be quoted on the command-line
- lines in prompt file should be of the form:
    ('amser035', "Mae hi ychydig wedi chwarter i hanner nos.")
- segInter assumes that the first and last segments in the textGrid are silence.
    """)
    
if __name__ == '__main__':
    import getopt, sys
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'd:f:i:l:')
        oDict = dict(options)
        if args and oDict.get('-f'):
            segInter(oDict['-f'], args, oDict.get('-l', 'Word'))
        elif oDict.get('-d') and oDict.get('-i'):
            transDict = json.load(open(oDict['-i']))['transDict']
            segInterDir(oDict['-d'], transDict, oDict.get('-l', 'Word'))
        else:
            printUsage()
    else:
        printUsage()
