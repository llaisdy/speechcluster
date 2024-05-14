#! /usr/bin/env python

# Copyright (c) 2005, University of Wales, Bangor 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#   * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#   * Neither the name of the University of Wales, Bangor nor the names
# of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



"""
* segFake: fake autosegmentation

** TODO

"""

from speechCluster import *

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
    print"""
segFake.py: fake autosegmentation.  Usage:
segFake.py -f <filename> -o (TextGrid | esps ) <phones>

    e.g.:
    segFake.py -f amser012.wav -o TextGrid \
    m ai hh ii n y n j o n b y m m y n y d w e d i yy n y b o r @

segFake -d <dirname> -t <transcription.fn> -o (TextGrid | esps )
    e.g.:
    segFake.py -d wav -t trans.txt -o TextGrid \

Transcription files should be one transcription per line, of the form:
    (amser012 "m ai hh i n y n j o n b y m m y n y d w e d i yy n @ b o r e.")

Output Formats supported:
  Format            File Extension(s)
  ======            =================
  esps              .esps, .lab, .seg
  TextGrid (Praat)  .TextGrid
  htk               .htk-lab, .htk-mlf


    
"""
    
if __name__ == '__main__':
    import getopt, sys
    options, args = getopt.getopt(sys.argv[1:], 'd:f:t:o:')
    oDict = dict(options)
    if oDict.get('-f') and oDict.get('-o'):
        wavFn = oDict['-f']
        outFormat = oDict['-o']
        seg = fakeLabel(wavFn, args, outFormat)
        segFn = '%s.%s' % (os.path.splitext(wavFn)[0], outFormat)
        open('%s' % segFn, 'w').write(seg)
    elif oDict.get('-d') and oDict.get('-t') and oDict.get('-o'):
        wavDir = oDict['-d']
        transFn = oDict['-t']
        outFormat = oDict['-o']
        for line in list(open(transFn)):
            phonData = line[1:-2].replace('.', '').replace('"', '').split()
            fstem = phonData.pop(0)
            wavFn = '%s/%s.wav' % (wavDir, fstem)
            seg = fakeLabel(wavFn, phonData, outFormat)
            segFn = '%s.%s' % (fstem, outFormat)
            open('%s/%s' % (wavDir, segFn), 'w').write(seg)
    else:
        printUsage()
