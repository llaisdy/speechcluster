import math
import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.splitAll import splitAll, parseCommandLine

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
        s1 = SpeechCluster(os.path.join(self.test_dir, f'{FSTEM_1}.TextGrid'))
        lab_fns_out = [
            fn for fn in sorted(os.listdir(self.out_dir))
            if os.path.splitext(fn)[1] == '.esps'
        ]
        self.assertEqual(len(lab_fns_out), math.ceil(s1.dataMax / step))

    def test_legacy_splitAll(self):
        level = 'Phone'
        testCommands = [
            # into 5 phone chunks:
            (f'splitAll.py -n 5 -t {level} testData fivePhones', 25),
            # by each word: see test_split_by_word above
            # by each silence:
            (f'splitAll.py -n 1 -t {level} -l sil testData bySilence', 21),
            # into 5 sec chunks: see test_split_by_time above
        ]
        for (cmd, expected) in testCommands:
            argv = cmd.split()[1:]
            splitCriteria, _inDir, outDir = parseCommandLine(argv)
            outDir = os.path.join(self.out_dir, outDir)
            if not os.path.exists(outDir):
                os.mkdir(outDir)
            splitAll(splitCriteria, self.test_dir, outDir)
            lab_fns_out = [
                fn for fn in sorted(os.listdir(outDir))
                if os.path.splitext(fn)[1] == '.esps'
            ]
            self.assertEqual(len(lab_fns_out), expected)

if __name__ == '__main__':
    unittest.main()
