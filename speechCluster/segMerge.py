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
* segMerge: merges label files

** TODO

"""

import os
from speechCluster import SpeechCluster

def segMerge(argList, debug=False):
    """segMerge: Merges several label files into one
    (e.g., for comparison).
    Each element of fnList should be a tuple:
    (filename, new label for tier)
    """
    fnList = [(argList[i], argList[i+1])
              for i in range(0, len(argList), 2)]
    print fnList
    topFn, topLabel = fnList.pop(0)
    seg = SpeechCluster(topFn, debug)
    seg.tiers[0].setName(topLabel)
    for fn in fnList:
        seg2 = SpeechCluster(fn[0], debug)
        seg2.tiers[0].setName(fn[1])
        seg.merge(seg2)
    stem, ext = os.path.splitext(topFn)
    saveFn = '%s_merge%s' % (stem, ext)
    open(saveFn, 'w').write(seg.write_format())


def printUsage():
    print """
* segMerge: Label file mergerer.

Merges label files into one multi-tiered label file, for example to compare different segmentations of a speech file.

n.b.: Currently only works on textGrids (and takes first tier of multi-tiered textGrids).

** Usage:

  segMerge.py <fn1> <tierName> <fn2> <tierName> <fn3> <tierName> ...

for example:

  segMerge.py eg1.TextGrid Me eg2.TextGrid Them eg2.TextGrid Fake ...


"""
    
if __name__ == '__main__':
    ## TODO: write command line switches (inc debug switch)
    from pprint import pprint

### segMerge works
    import sys
    if len(sys.argv) > 2:
        args = sys.argv[1:]
        segMerge(args)
    else:
        printUsage()
