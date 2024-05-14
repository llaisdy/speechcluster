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
* segReplace: replace labels in a label file

** TODO

"""

import os
from speechCluster import SpeechCluster

def segReplace(replaceDict, fn, debug=False):
    spcl = SpeechCluster(fn, debug)
    spcl.replaceLabs(replaceDict)
    outFormat = os.path.splitext(fn)[1][1:] # without the dot
    out = spcl.write_format(outFormat)
    open(fn, 'w').write(out)

def segReplaceDir(dir, replaceDict, debug=False):
    os.chdir(dir)
    for fn in os.listdir(os.getcwd()):
        segReplace(replaceDict, fn, debug)
        print 'Done ', fn

def printUsage():
    print """
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


"""
    
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

