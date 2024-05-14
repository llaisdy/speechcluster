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
* segInter: interpolates labels into an empty segmentation tier

** TODO

"""

from speechCluster import *

def segInter(fn, labList, level='Word'):
    seg = SpeechCluster(fn)
    tier = seg.getTierByName(level)
    labList = prepLabs(labList)
    for segment in tier:
        if segment.label == '':
            segment.label = labList.pop(0)
    open(fn, 'w').write(seg.write_format())


def segInterDir(dir, promptFn, level='Word'):
    items = parsePromptFn(promptFn)
    import os
    os.chdir(dir)
    for i in items:
        segInter(i[0], i[1], level)

def parsePromptFn(promptFn):
    items = []
    data = list(open(promptFn))
    for line in data:
        line = line[1:-2] # strip off brackets and newline
        ll = line.split()
        fn = '%s.TextGrid' % ll.pop(0) # only textgrids supported
        #labList = prepLabs(' '.join(ll))
        items.append((fn, ll))
    return items

def prepLabs(labList):
    if labList[0][0] in ['"', "'"]: # remove quotes
        labList[0] = labList[0][1:]
        labList[-1] = labList[-1][:-1]
    if labList[-1][-1] in ['.', '!', '?']:
        labList[-1] = labList[-1][:-1] # remove final punct
    labList.insert(0, 'sil')
    labList.append('sil')
    return labList

def printUsage():
    print """segInter.py: Interpolates labels into label file

Usage:

  segInter.py [-l <level>] -f <label filename> <labels>

    e.g.: segInter.py -f amser035.TextGrid Mae hi ychydig wedi chwarter i hanner nos

  segInter.py [-l <level>] -d <dir> -i <prompt filename>

    e.g.: segInter.py -d lab -i amser.data

#### silence or no silence? ####


Notes:

- only TextGrid label format is supported
- the default level/tierName is 'Word'
- labels do not have to be quoted on the command-line
- lines in prompt file should be of the form:
    ('amser035', "Mae hi ychydig wedi chwarter i hanner nos.")
- segInter assumes that the first and last segments in the textGrid are silence.
    """
    
if __name__ == '__main__':
    from pprint import pprint

    import getopt, sys
    if len(sys.argv) > 1:
        options, args = getopt.getopt(sys.argv[1:], 'd:f:i:l:')
        oDict = dict(options)
        if args and oDict.get('-f'):
            segInter(oDict['-f'], args, oDict.get('-l', 'Word'))
        elif oDict.get('-d') and oDict.get('-i'):
            segInterDir(oDict['-d'], oDict['-i'], oDict.get('-l', 'Word'))
        else:
            printUsage()
    else:
        printUsage()
