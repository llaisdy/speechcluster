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
* segSwitch: Label file converter.

See documentation for SpeechCluster for which formats are supported,
and to what extent.

"""

import os
from speechCluster import *

def segSwitch(inFn, outFn, debug=False):
    """
Args: string inFn: input filename
      string outFn: output filename
      bool  debug(=False): provides error messages if True
Returns: None

Uses filename extensions to find out input & output formats.  
    """
    if os.path.splitext(inFn)[1] == '.mlf': # htk master label file
        ### TODO: put this into speechCluster when it works
        outFormat = SpeechCluster.formatDict['.%s' % outFn.lower()]
        labFiles = list(open(inFn))[1:]
        while labFiles:
            idx = labFiles.index('.\n')
            labList = labFiles[:idx]
            labFiles = labFiles[idx+1:]
            fstem = labList.pop(0)[1:]
            fstem = os.path.splitext(os.path.basename(fstem))[0]
            fn = '%s.%s' % (fstem, outFormat)
            spcl = SpeechCluster()
            tier = SegmentationTier()
            for lab in labList:
                fields = lab.split()[:3]
                seg = Segment()
                seg.min = eval(fields[0])/10000000.0
                seg.max = eval(fields[1])/10000000.0
                seg.label = fields[2]
                tier.append(seg)
            tier.setName('Phone') # TODO: Magic text!!
            spcl.updateTiers(tier)
            out = spcl.write_format(outFormat)
            open(fn, 'w').write(out)
    else:
        spcl = SpeechCluster(inFn, debug)
        ofext = os.path.splitext(outFn)[1]
        outFormat = SpeechCluster.formatDict[ofext.lower()]
        out = spcl.write_format(outFormat)
        open(outFn, 'w').write(out)

def segSwitchDir(dir, outFormat, debug=False):
    """
Args: string dir: directory name
      string outFormat: extension for output format
      bool debug(=False): provides error messages if True
Returns: None

Runs segSwitch for each file in <dir>.  Files are output in <dir>
as filename.<outFormat>
    """
    home = os.path.abspath(os.getcwd())
    os.chdir(dir)
    if outFormat in ['htk-mlf', 'mlf']:
        outFormat = 'mlf'
        out = '#!MLF!#\n'
        for inFn in os.listdir(os.getcwd()):
            spcl = SpeechCluster(inFn, debug)
            this = spcl.write_format('htk-lab')
            open('%s.lab'% os.path.splitext(inFn)[0], 'w').write(this)
            out = '%s%s' % (out, this)
        open('htk_labels.%s' % outFormat, 'w').write(out)
    else:
        for inFn in os.listdir(os.getcwd()):
            outFn = '%s.%s' % (os.path.splitext(inFn)[0], outFormat)
            segSwitch(inFn, outFn)
    os.chdir(home)
        

def printUsage():
    print """\
* segSwitch.py Label file converter.
    
Usage:
  segSwitch -i <infilename> -o <outfilename>
  segSwitch -i <infilestem>.mlf -o <outFormat>
  segSwitch -d <dirname> -o <outFormat>

Formats supported:
  Format                  File Extension(s)
  ======                  =================
  esps                    .esps, .lab, .seg
  Praat TextGrid          .TextGrid
  htk label file          .htk-lab
  htk master label file   .htk-mlf
  htk transcription       .htk-grm

n.b.: currently, segSwitch will only convert *into* not *out of* htk-grm format.

"""
    
if __name__ == '__main__':
    import getopt, sys
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'd:i:o:')
        oDict = dict(options)
        if oDict.get('-i') and oDict.get('-o'):
            segSwitch(oDict['-i'], oDict['-o'])
        elif oDict.get('-d') and oDict.get('-o'):
            segSwitchDir(oDict['-d'], oDict['-o'])
        else: printUsage()
    else:
        printUsage()
