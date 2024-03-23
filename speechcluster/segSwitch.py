#! /usr/bin/env python3

"""
* segSwitch: Label file converter.

See documentation for SpeechCluster for which formats are supported,
and to what extent.

"""

import os
from .speechCluster import *
from.utils import file_write

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
            file_write(fn, out)
    else:
        spcl = SpeechCluster(inFn, debug)
        ofext = os.path.splitext(outFn)[1]
        outFormat = SpeechCluster.formatDict[ofext.lower()]
        out = spcl.write_format(outFormat)
        file_write(outFn, out)

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
            file_write(f'{os.path.splitext(inFn)[0]}.lab', this)
            out = '%s%s' % (out, this)
        file_write(f'htk_labels.{outFormat}', out)
    else:
        for inFn in os.listdir(os.getcwd()):
            outFn = '%s.%s' % (os.path.splitext(inFn)[0], outFormat)
            segSwitch(inFn, outFn)
    os.chdir(home)
        

def printUsage():
    print("""\
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

""")
    
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
