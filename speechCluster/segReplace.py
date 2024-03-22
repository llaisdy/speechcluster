#! /usr/bin/env python3


"""
* segReplace: replace labels in a label file

** TODO

"""

import os
from speechCluster import SpeechCluster

def segReplace(replaceDict, fn, debug=False):
    spcl = SpeechCluster(fn, debug)
    if spcl.segFormat not in [None, 'wav']: # skip unsupported formats
        spcl.replaceLabs(replaceDict)
        outFormat = os.path.splitext(fn)[1][1:] # without the dot
        out = spcl.write_format(outFormat)
        open(fn, 'w').write(out)

def segReplaceDir(dir, replaceDict, debug=False):
    os.chdir(dir)
    for fn in os.listdir(os.getcwd()):
        segReplace(replaceDict, fn, debug)
        print(f'Done {fn}')

def printUsage():
    print("""
* segReplace.py: Label file label converter.

Usage:
  segReplace -r <replaceDict filename> <segfilename>
  segReplace -r <replaceDict filename> -d <dirname>

ReplaceDict Format:

File should contain the following:

replaceDict = {'oldLabel1': 'newLabel1',
               'oldLabel2': 'newLabel2',
               'oldLabel3': 'newLabel3',
               'oldLabel4': 'newLabel4',
               ...
               }

n.b.:
- Quote marks are required;
- If an oldLabel has '!!merge' as its newLabel, segments with that label are merged with the previous segment (i.e., the segment is removed, and the previous label's end time is extended).
- oldLabels can be longer than a single label.  Currently they can be no longer than two labels, e.g., 't sh'.


""")
    
if __name__ == '__main__':
    import getopt, sys
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'd:r:')
        oDict = dict(options)
        if oDict.get('-r'):
            replaceDictFn = oDict['-r']
            exec(open(replaceDictFn).read())
            if oDict.get('-d'):
                segReplaceDir(oDict['-d'], replaceDict)
            else:
                fn = args[0]
                segReplace(replaceDict, fn)
        else: printUsage()
    else:
        printUsage()

