#! /usr/bin/env python3


"""
* segMerge: merges label files

** TODO

"""

import os
from .speechCluster import SpeechCluster

def segMerge(argList, debug=False):
    """segMerge: Merges several label files into one
    (e.g., for comparison).
    Each element of fnList should be a tuple:
    (filename, new label for tier)
    """
    fnList = [(argList[i], argList[i+1])
              for i in range(0, len(argList), 2)]
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
    print("""
* segMerge: Label file mergerer.

Merges label files into one multi-tiered label file, for example to compare different segmentations of a speech file.

n.b.: Currently only works on textGrids (and takes first tier of multi-tiered textGrids).

** Usage:

  segMerge.py <fn1> <tierName> <fn2> <tierName> <fn3> <tierName> ...

for example:

  segMerge.py eg1.TextGrid Me eg2.TextGrid Them eg2.TextGrid Fake ...


""")

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
