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
* trim: trims beginning and end silence from SpeechClusters

** TODO

"""

from speechCluster import *

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
    print newStart, newEnd
    sc.setStartEnd(newStart, newEnd)
    sc.write_wav()
    if '.' not in fn: # must be a filestem
        open('%s_tr.TextGrid' % fn, 'w').write(sc.write_TextGrid())
    


def printUsage():
    print"""
* trim.py: wav file trimmer

Trims beginning and end silence from wav files, adjusts any associated label files accordingly.

** Usage

trim.py -p 1.5 example.wav  # trims example.wav leaving 1.5s padding
trim.py -p 1.5 example  # as above, adjusts any seg files found too 

trim.py -d testdir  # trims all files in testdir, including any seg files,
                    # leaving .5s padding

    
"""
    
if __name__ == '__main__':
    import getopt, os, sys
    options, args = getopt.getopt(sys.argv[1:], 'd:p:')
    oDict = dict(options)
    if len(args) == 1:
        if '-p' not in oDict:
            pad = 0.5
        else:
            pad = eval(oDict['-p'])
        if oDict.get('-d'):
            import os
            wdir = oDict['-d']
            fns = os.listdir(wdir)
            os.chdir(wdir)
            fstems = {}
            for fstem in [os.path.splitext(fn)[0]
                          for fn in os.listdir(os.getcwd())]:
                fstems.setdefault(fstem, []).append(1)
            for fstem in fstems:
                print fstem
                print fstems[fstem]
                if len(fstems[fstem]) == 1:
                    fstem = '%s.wav' % fstem
                trim(fstem, pad)
        else:
            fn = args[0]
            trim(fn, pad)
    else:
        printUsage()
