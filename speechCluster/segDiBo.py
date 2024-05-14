#! /usr/bin/python

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
* segDiBo: explicit diphone boundary marker

** TODO
- this file is full of magic text!

"""

import audioop, copy, wave
from speechCluster import *

# magic text
# stops and vowels wouldn't be necessary
# if we had phone objects!
stops = {'p': 0.0180,
	 't': 0.0300,
	 'k': 0.0150,
	 'b': 0.0140,
	 'd': 0.0250,
         'g': 0.0100}

vowels = 'aeiouy'




dbLabel = 'DB'
silenceLabel = 'sil'
phoneTier = 'Phone'

def segDiBo(fstem):
    print '* %s\n' % fstem
    spcl = SpeechCluster(fstem)
    spcl.getPitchmarks()
    tier = spcl.getTierByName(phoneTier)
    newtier = copy.copy(tier)

    # do stops
    for seg in tier:
        if seg.label in stops:
            #print '**  %s  ------------------------------\n' % seg.label
            start, stop = findQuiet(spcl, seg)
            t = (start + stop) / 2.0
            #### t = spcl.getNearestOptimum(t)
            ## not appropriate for DBs in stop closures
            dbSeg = Segment()
            dbSeg.label = dbLabel
            dbSeg.min = seg.min
            dbSeg.max = t
            nSeg = Segment()
            nSeg.label = seg.label
            nSeg.min = t
            nSeg.max = seg.max
            # if previous seg = 'sil'?
            prevSeg = tier[tier.index(seg)-1]
            if prevSeg.label == silenceLabel:
                dbSeg.min += dbSeg.max - dbSeg.min - stops[seg.label]
                nSilSeg = Segment()
                nSilSeg.label = silenceLabel
                nSilSeg.min = prevSeg.min
                nSilSeg.max = dbSeg.min
                newtier.remove(prevSeg)
                newtier.insertSegment(nSilSeg)
            newtier.remove(seg)
            newtier.insertSegment(dbSeg)
            newtier.insertSegment(nSeg)

    # do vowel-silence
    for i in range(1, len(tier)):
        if tier[i].label == silenceLabel:
            if tier[i-1].label[0] in vowels:
                seg = tier[i-1]
                t = seg.min + ((seg.max - seg.min)/5.0)
                dbSeg = Segment()
                dbSeg.label = dbLabel
                dbSeg.min = seg.min
                dbSeg.max = t
                nSeg = Segment()
                nSeg.label = seg.label
                nSeg.min = t
                nSeg.max = seg.max
                newtier.remove(seg)
                newtier.insertSegment(dbSeg)
                newtier.insertSegment(nSeg)
                
    # do initial extra silences
    newtier.pop(0)
    sil = Segment()
    sil.label = silenceLabel
    sil.max = newtier[0].min
    sil.min = max((sil.max - 0.2), 0.0)
    newtier.insertSegment(sil)
    if sil.min > 0:
        sil = Segment()
        sil.label = silenceLabel
        sil.max = newtier[0].min
        sil.min = 0
        newtier.insertSegment(sil)
    # do final extra silences
    dataEnd = newtier[-1].max
    newtier.pop()
    sil = Segment()
    sil.label = silenceLabel
    sil.min = newtier[-1].max
    sil.max = min((sil.min + 0.2), dataEnd)
    newtier.insertSegment(sil)
    if sil.max < dataEnd:
        sil = Segment()
        sil.label = silenceLabel
        sil.min = newtier[-1].max
        sil.max = dataEnd
        newtier.insertSegment(sil)

    # move DB boundaries to nearest optimum
    # TODO: t = spcl.getNearestOptimum(t)
    for i in range(len(newtier)):
        if newtier[i].label == dbLabel:
            seg = newtier[i]
            t = spcl.getNearestOptimum(seg.max)
            if abs(t - seg.max) < 0.01:
                newtier[i].max = t
                newtier[i+1].min = t
    
    # save
    spcl.tiers.remove(tier)
    spcl.updateTiers(newtier)
    out = spcl.write_TextGrid()
##     print out
    open('%s_dibo.TextGrid' % spcl.fstem, 'w').write(out)

    

def findQuiet(spcl, seg, windowSize=0.01):
        noiseTimes = []
        quietTimes = []
        data = wave.open(spcl.audioFn)
        width = data.getsampwidth()
        frate = data.getframerate()
        nframes = data.getnframes()
        endTime = nframes*1.0/frate
        segBegin = int(seg.min * frate)
        segNframes = int((seg.max - seg.min) * frate)
        data.setpos(segBegin)
        rmsFull = audioop.rms(data.readframes(segNframes), width)
        #print 'rmsFull = ', rmsFull
        data.setpos(segBegin)
        window = int(frate*windowSize)
        step = window/2
        while data.tell() < segBegin + segNframes - step:
            sample = data.readframes(window)
            rms = audioop.rms(sample, width)
            now = data.tell()*1.0/(frate)
            if rms > rmsFull/10:
                noiseTimes.append(now)
                #print '%6d\t%s\tNoise' % (rms, now)
            else:
                quietTimes.append(now)
                #print '%6d\t%s\tQuiet' % (rms, now)
            data.setpos(data.tell()-step)
        if len(quietTimes) < len(noiseTimes)/2:
            print '*** WARNING: %s :: / %s /' % (spcl.fstem, seg.label)
        if not len(quietTimes):
            print '    DOUBLE WARNING: NO QUIET AT ALL!'
            quietTimes.append(seg.min)
            t = seg.min + ((seg.max - seg.min) / 4.0)
            quietTimes.append(t)
##         pprint(quietTimes)
        print
        return (quietTimes[0], quietTimes[-1])
            
def printUsage(): print """\
* segDiBo.py add diphone boundaries

segDiBo adds explicit diphone boundaries to label files, ready for use in festival diphone synthesis.  It also outputs pitchmark (pm) files.  segDiBo'd label files (fstem_dibo.ext) and pm files are output into the given data directory.

** Usage

segDiBo.py -d <dataDirectory>



"""

if __name__ == '__main__':
    from pprint import pprint
    import getopt, os, sys
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'd:i:o:')
        oDict = dict(options)
        if oDict.get('-d'):
            testDir = oDict['-d']
    else:
        testDir = 'test'
    fstems = [os.path.splitext(fn)[0]
              for fn in os.listdir(testDir)
              if os.path.splitext(fn)[1] == '.wav']
    os.chdir(testDir)
    for fstem in fstems:
        segDiBo(fstem)
        #segDiBo(os.path.join(testDir, fstem))

    
