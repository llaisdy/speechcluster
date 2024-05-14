#! /usr/bin/python2.3

import os, sys
from segReplace import *

"""

"""

replaceDict = {'tbst': '!!merge',
               't sh': 'ch',
               'ax': '@'}

if __name__ == '__main__':
    inDir = 'dataDir' # sys.argv[1]
    segReplaceDir(inDir, replaceDict)

