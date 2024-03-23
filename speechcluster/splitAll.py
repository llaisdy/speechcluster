#! /usr/bin/env python3

"""
* splitAll: split up SPeechClusters by given criteria

** TODO

"""

import os
from .speechCluster import *

def optionList2criteriaDict(optList):
    """takes option list in format e.g.,
    [('-n', '5'), ('-t', 'Phone'), ('-l', 'sil')]
    returns dict in format e.g.,
    {'n': 1, 'tier': 'Phone', 'label': 'sil'}
    """
    optDict = dict(optList)
    cDict = {}
    cDict['n'] = int(optDict['-n'])
    cDict['tier'] = optDict['-t']
    cDict['label'] = optDict.get('-l', '') # optional option
    return cDict

def splitAll(splitCriteria, inDir, outDir):
    stems = getStems(inDir)
    for stem in stems:
        fullstem = '%s%s%s' % (inDir, os.path.sep, stem)
        spcl = SpeechCluster(fullstem, True)
        spcl.split(splitCriteria, outDir)

def getStems(inDir):
    return uniq([os.path.splitext(fn)[0]
                 for fn in os.listdir(inDir)])

def uniq(inList):
    a = []
    for i in inList:
        if i not in a:
            a.append(i)
    return a

def printUsage():
    print("""\

* splitAll.py label/audio pair splitter

Usage: splitAll.py -n <integer> -t <tierName> [-l <label>] inDir outDir

inDir should contain pairs of speech audio and label files (e.g., wav and TextGrid).  splitAll will split each pair into shorter paired segments, based on the parameters given.

Examples:                                 # splits ...

splitAll.py -n 5 -t Phone in/ out/        # into 5 phone chunks

splitAll.py -n 1 -t Word in/ out/         # by each word

splitAll.py -n 1 -t Phone -l sil in/ out/ # by each silence

splitAll.py -n 5 -t Second in/ out/       # into 5 sec chunks

    """)

def parseCommandLine(argList):
    import getopt
    options, args = getopt.getopt(argList, 'n:t:l:o:')
    outDir = args.pop()
    inDir = args.pop()
    splitCriteria = optionList2criteriaDict(options)
    return splitCriteria, inDir, outDir

if __name__ == '__main__':
    import sys
    argv = sys.argv[1:]
    if len(argv) < 6: printUsage()
    else:
        from pprint import pprint
        splitCriteria, inDir, outDir = parseCommandLine(argv)
        print('Split Criteria:\n  ',)
        pprint(splitCriteria)
        splitAll(splitCriteria, inDir, outDir)
