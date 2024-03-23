#! /usr/bin/env python3

"""
* trim: trims beginning and end silence from SpeechClusters

** TODO

"""

from .speechCluster import *

def trim(fn, pad):
    sc = SpeechCluster(fn)
    segStart, segEnd, fileEnd = sc.getStartEnd()
    if pad <= segStart:
        newStart = segStart - pad
    else:
        newStart = segStart
    if pad <= (fileEnd - segEnd):
        newEnd = segEnd + pad
    else:
        newEnd = fileEnd
    print(f'new start: {newStart}, new end: {newEnd}')
    sc.setStartEnd(newStart, newEnd)
    sc.write_wav()
    if '.' not in fn: # must be a filestem
        open('%s_tr.TextGrid' % fn, 'w').write(sc.write_TextGrid())
    


def printUsage():
    print("""
* trim.py: wav file trimmer

Trims beginning and end silence from wav files, adjusts any associated label files accordingly.

** Usage

trim.py -p 1.5 example.wav  # trims example.wav leaving 1.5s padding
trim.py -p 1.5 example  # as above, adjusts any seg files found too 

trim.py -d testdir  # trims all files in testdir, including any seg files,
                    # leaving .5s padding

    
""")

def trimDir(wdir, pad):
    import os
    fns = os.listdir(wdir)
    os.chdir(wdir)
    fstems = {}
    for fstem in [os.path.splitext(fn)[0]
                  for fn in os.listdir(os.getcwd())]:
        fstems.setdefault(fstem, []).append(1)
    for fstem in fstems:
        print(fstem)
        print(fstems[fstem])
        if len(fstems[fstem]) == 1:
            fstem = '%s.wav' % fstem
        trim(fstem, pad)

if __name__ == '__main__':
    import getopt, os, sys
    options, args = getopt.getopt(sys.argv[1:], 'd:p:')
    oDict = dict(options)
    if len(args) == 1 or '-d' in oDict:
        if '-p' not in oDict:
            pad = 0.5
        else:
            pad = eval(oDict['-p'])
        if oDict.get('-d'):
            wdir = oDict['-d']
            trimDir(wdir, pad)
        else:
            fn = args[0]
            trim(fn, pad)
    else:
        printUsage()
