#! /usr/bin/python2.3

import os, sys
from segSwitch import *

"""
  segSwitch -i <infilename> -o <outfilename>
  segSwitch -i <infilestem>.mlf -o <outFormat>
  segSwitch -d <dirname> -o <outFormat>

"""

supportedFormats = ['lab', 'TextGrid', 'htk-lab', 'htk-mlf', 'htk-grm']


def test(inDir='', outDir='segSwitch__test'):
    """
    """
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    print '* SegSwitch Tests\n'

    # get the format(s) of in_d files
    formatList = [os.path.splitext(fn)[1][1:]
                  for fn in os.listdir(inDir)]
    formatDict = {}
    for f in formatList:
        formatDict.setdefault(f, 0)
    formatList = formatDict.keys()

    print 'Input formats: %s\n' % ', '.join(formatList)
    if len(formatList) > 1:
        print 'Please ensure all input files are the same format.'
        return
    inFormat = formatList[0]
    outFormats = [f for f in supportedFormats
                  if f != inFormat]
    print 'Output formats: %s\n' % ', '.join(outFormats)

    # segSwitch those into outDir dirs

    testCycle(inDir, inFormat, outDir, outFormats)

    # foreach outDir dir:
    # segSwitch those into the other three formats

    while len(outFormats) > 1:
        inFormat = outFormats.pop(0)
        testCycle(inDir, inFormat, outDir, outFormats)
        
    # open(os.path.join(outDir, 'report.txt'), 'w').write(report)

def testCycle(inDir, inFormat, outDir, outFormats):
    for i in range(len(outFormats)):
        thisOut = outFormats[i]
        print '** SegSwitch %s --> %s ...' % (inFormat, thisOut),
        segSwitchDir(inDir, thisOut) 
        dirname = os.path.join(outDir, '%s_2_%s' % (inFormat, thisOut))
        os.mkdir(dirname)
        for f in [f for f in os.listdir(inDir)
                  if os.path.splitext(f)[1][1:] == thisOut]:
            os.rename(os.path.join(inDir, f),
                      os.path.join(dirname, f))
        print 'OK\n'
    

if __name__ == '__main__':
    inDir = 'dataDir' # sys.argv[1]
    test(inDir)

