import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.segSwitch import segSwitch, segSwitchDir


DATA_DIR = 'tests/data'
PRIV_DIR = 'tests/priv'
FSTEM_1 = 'cven_for_replace'

def setUpModule():
    os.mkdir(PRIV_DIR)

def tearDownModule():
    shutil.rmtree(PRIV_DIR)
    pass

class SwitchTestCase(unittest.TestCase):
    def setUp(self):
        self.textgrid_fn = f'{FSTEM_1}.TextGrid'
        shutil.copy(os.path.join(DATA_DIR, self.textgrid_fn), PRIV_DIR)
        
    def tearDown(self):
        [os.remove(os.path.join(PRIV_DIR, fn)) for fn in os.listdir(PRIV_DIR)]
        pass

    def test_segSwitch(self):
        fn_in = os.path.join(PRIV_DIR, self.textgrid_fn)
        fn_out = os.path.join(PRIV_DIR, f'{FSTEM_1}.lab')
        level = 'Phone'
        s1 = SpeechCluster(fn_in)
        s1labs = [s.label for s in s1.getTierByName(level)]
        segSwitch(fn_in, fn_out)
        s2 = SpeechCluster(fn_out)
        s2labs = [s.label for s in s2.tiers[0]]
        self.assertEqual('esps', s2.segFormat)
        self.assertEqual(s1labs, s2labs)
        s3 = SpeechCluster(fn_in)
        self.assertEqual('TextGrid', s3.segFormat)

if __name__ == '__main__':
    unittest.main()
