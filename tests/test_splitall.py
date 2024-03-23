import math
import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.splitAll import splitAll

DATA_DIR = 'tests/data'
PRIV_DIR = 'tests/priv'
FSTEM_1 = 'cven_for_splitall'

def setUpModule():
    os.mkdir(PRIV_DIR)

def tearDownModule():
    shutil.rmtree(PRIV_DIR)
    pass

class SplitAllTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(PRIV_DIR, 'for_splitall')
        self.out_dir = os.path.join(PRIV_DIR, 'for_splitall_out')
        os.mkdir(self.test_dir)
        os.mkdir(self.out_dir)
        [shutil.copy(os.path.join(DATA_DIR, f'{FSTEM_1}.{ext}'), self.test_dir)
         for ext in ['TextGrid', 'wav']]
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.out_dir)
        pass

    def test_split_by_word(self):
        level = 'Word'
        splitCriteria = {
            'n': 1,
            'tier': level,
        }
        splitAll(splitCriteria, self.test_dir, self.out_dir)
        # one output label file for each Word
        s1 = SpeechCluster(os.path.join(self.test_dir, f'{FSTEM_1}.TextGrid'))
        s1segs = s1.getTierByName(level)
        lab_fns_out = [
            fn for fn in sorted(os.listdir(self.out_dir))
            if os.path.splitext(fn)[1] == '.esps'
        ]
        self.assertEqual(len(lab_fns_out), len(s1segs))

    def test_split_by_time(self):
        step = 1
        splitCriteria = {
            'n': 5,
            'step': step,
            'tier': 'sec',
        }
        splitAll(splitCriteria, self.test_dir, self.out_dir)
        # TODO what to assert?
        s1 = SpeechCluster(os.path.join(self.test_dir, f'{FSTEM_1}.TextGrid'))
        lab_fns_out = [
            fn for fn in sorted(os.listdir(self.out_dir))
            if os.path.splitext(fn)[1] == '.esps'
        ]
        self.assertEqual(len(lab_fns_out), math.ceil(s1.dataMax / step))


def legacy_test_prev(in_d='', out_d='splitAll__test'):
    if out_d and not os.path.exists(out_d):
        os.mkdir(out_d)
    report = '* SplitAll Tests\n\n'
    testCommands = [
        # into 5 phone chunks
        'splitAll.py -n 5 -t Phone testData fivePhones',
        # by each word -- see above
        # by each silence
        'splitAll.py -n 1 -t Phone -l sil testData bySilence',
        # into 5 sec chunks -- see above
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
    unittest.main()
