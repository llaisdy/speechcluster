#! /usr/bin/env python3

"""
* segFake: fake autosegmentation

** TODO

"""

import json

from .speechCluster import *
from .utils import set_directory

def fakeLabel(fn, phoneList, outFormat='TextGrid'):
    seg = SpeechCluster(fn)
    segStart, segEnd, fileEnd = seg.getStartEnd()
    width = (segEnd - segStart)*1.0 / len(phoneList)
    tier = SegmentationTier()
    # start with silence
    x = Segment()
    x.min = 0
    x.max = segStart
    x.label = 'sil'
    tier.append(x)
    for i in range(len(phoneList)):
        x = Segment()
        x.label = phoneList[i]
        x.min = tier[-1].max
        x.max = x.min + width
        tier.append(x)
    # end with silence
    x = Segment()
    x.min = tier[-1].max
    x.max = fileEnd
    x.label = 'sil'
    tier.append(x)
    tier.setName('Phone') # TODO: Magic text!!
    seg.updateTiers(tier)
    outFormat = SpeechCluster.formatDict['.%s' % outFormat.lower()]
    return seg.write_format(outFormat)

def printUsage():
    print("""
segFake.py: fake autosegmentation.  Usage:
segFake.py -f <filename> -o (TextGrid | esps ) <phones>

    e.g.:
    segFake.py -f amser012.wav -o TextGrid \
    m ai hh ii n y n j o n b y m m y n y d w e d i yy n y b o r @

segFake -d <dirname> -t <transcription.fn> -o (TextGrid | esps )
    e.g.:
    segFake.py -d wav -c context.json -o TextGrid \

context.json should contain a "transDict" object with key value pairs like this:

    {"transDict": {
        "amser012": "m ai hh i n y n j o n b y m m y n y d w e d i yy n @ b o r e.",
        ...
       }
    }

Output Formats supported:
  Format            File Extension(s)
  ======            =================
  esps              .esps, .lab, .seg
  TextGrid (Praat)  .TextGrid
  htk               .htk-lab, .htk-mlf
    
""")

def fakeLabel_and_write(wavFn, phonData, outFormat):
    seg = fakeLabel(wavFn, phonData, outFormat)
    fstem = os.path.splitext(wavFn)[0]
    segFn = '%s.%s' % (fstem, outFormat)
    with open(segFn, 'w') as f:
        f.write(seg)


def fakeLabel_and_write_dir(wavDir, transDict, outFormat):
    lines = list(transDict.items())
    with set_directory(wavDir):
        for wavFn, phonData in lines:
            phonData = phonData.replace('.', '').replace('"', '').split()
            fakeLabel_and_write(wavFn, phonData, outFormat)
    
if __name__ == '__main__':
    import getopt, sys
    options, args = getopt.getopt(sys.argv[1:], 'd:f:c:o:')
    oDict = dict(options)
    if oDict.get('-f') and oDict.get('-o'):
        wavFn = oDict['-f']
        outFormat = oDict['-o']
        fakeLabel_and_write(wavFn, args, outFormat)
    elif oDict.get('-d') and oDict.get('-c') and oDict.get('-o'):
        wavDir = oDict['-d']
        transDict = json.load(open(oDict['-c']))['transDict']
        outFormat = oDict['-o']
        fakeLabel_and_write_dir(wavDir, transDict, outFormat)
    else:
        printUsage()
