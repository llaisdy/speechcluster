#! /usr/bin/python

import sys
from splitAll import *

def test(in_d='', out_d='splitAll__test'):
    """
    splitAll.py -n 5 -t Phone in/ out/        # into 5 phone chunks
    splitAll.py -n 1 -t Word in/ out/         # by each word
    splitAll.py -n 1 -t Phone -l sil in/ out/ # by each silence
    splitAll.py -n 5 -t Second in/ out/       # into 5 sec chunks
    """
    if out_d and not os.path.exists(out_d):
        os.mkdir(out_d)
    report = '* SplitAll Tests\n\n'
    testCommands = [
        'splitAll.py -n 5 -t Phone testData fivePhones',
        'splitAll.py -n 1 -t Word testData oneWord',
        'splitAll.py -n 1 -t Phone -l sil testData bySilence',
        'splitAll.py -n 5 -t Second testData fiveSecs'
        ]
    for cmd in testCommands:
        argv = cmd.split()[1:]
        splitCriteria, inDir, outDir = parseCommandLine(argv)
        report = '%s** %s\n\nSplit Criteria:\n' % (report, cmd)
        keys = splitCriteria.keys()
        keys.sort()
        for k in keys:
            report = "%s\t%s: '%s'\n" % (report, k, splitCriteria[k])
        report = '%s\n' % report
        if in_d:
            inDir = in_d
        if out_d:
            outDir = os.path.join(out_d, outDir)
        if not os.path.exists(outDir):
            os.mkdir(outDir)
        splitAll(splitCriteria, inDir, outDir)
    open(os.path.join(out_d, 'report.txt'), 'w').write(report)

if __name__ == '__main__':
    inDir = sys.argv[1]
    test(inDir)

