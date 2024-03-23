import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.segReplace import segReplace, segReplaceDir


DATA_DIR = 'tests/data'
PRIV_DIR = 'tests/priv'
FSTEM_1 = 'cven_for_replace'

def setUpModule():
    os.mkdir(PRIV_DIR)

def tearDownModule():
    shutil.rmtree(PRIV_DIR)
    pass

class ReplaceTestCase(unittest.TestCase):
    def setUp(self):
        self.textgrid_fn = f'{FSTEM_1}.TextGrid'
        shutil.copy(os.path.join(DATA_DIR, self.textgrid_fn), PRIV_DIR)
        
    def tearDown(self):
        [os.remove(os.path.join(PRIV_DIR, fn)) for fn in os.listdir(PRIV_DIR)]

    def test_segReplace(self):
        replaceDict = {'again': '!!merge', # [3]
                       't sh': 'ch',       # [
                       'nine': '9'}
        fn = os.path.join(PRIV_DIR, self.textgrid_fn)
        level = 'Phone'
        s1 = SpeechCluster(fn)
        s1segs = s1.getTierByName(level)
        segReplace(fn, replaceDict)
        s2 = SpeechCluster(fn)
        s2segs = s2.getTierByName(level)
        # again is merged
        self.assertEqual('again', s1segs[3].label)
        self.assertEqual(s1segs[2].min, s2segs[2].min)
        self.assertEqual(s1segs[3].max, s2segs[2].max)
        self.assertEqual(s1segs[4], s2segs[3])
        # t sh are merged into ch
        self.assertEqual('t', s1segs[5].label)
        self.assertEqual('sh', s1segs[6].label)
        self.assertEqual('ch', s2segs[4].label)
        self.assertEqual(s1segs[5].min, s2segs[4].min)
        self.assertEqual(s1segs[6].max, s2segs[4].max)
        # nine => 9
        self.assertEqual('nine', s1segs[9].label)
        self.assertEqual('9', s2segs[7].label)
        self.assertEqual(s1segs[9].min, s2segs[7].min)
        self.assertEqual(s1segs[9].max, s2segs[7].max)

if __name__ == '__main__':
    unittest.main()
