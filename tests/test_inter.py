import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.segInter import segInter, segInterDir

DATA_DIR = 'tests/data'
PRIV_DIR = 'tests/priv'
FSTEM_1 = 'common_voice_en_34926907'
FSTEM_2 = 'common_voice_en_35387333'
FSTEM_3 = 'common_voice_en_36528488'
FSTEMS = (FSTEM_1, FSTEM_2, FSTEM_3)

def setUpModule():
    os.mkdir(PRIV_DIR)

def tearDownModule():
    shutil.rmtree(PRIV_DIR)
    pass

class InterTestCase(unittest.TestCase):
    def setUp(self):
        self.textgrid_fn = tg_ready_for_inter(FSTEM_3, True)
        [shutil.copy(os.path.join(DATA_DIR,
                                  tg_ready_for_inter(fstem, True)),
                     PRIV_DIR)
         for fstem in FSTEMS]
        shutil.copy(os.path.join(DATA_DIR, self.textgrid_fn), PRIV_DIR)
        
    def tearDown(self):
        [os.remove(os.path.join(PRIV_DIR, fn)) for fn in os.listdir(PRIV_DIR)]

    def test_segInter(self):
        # segInter.py [-l <level>] -f <label filename> <labels...>
        # assumes tier already exists with empty segments
        fn = os.path.join(PRIV_DIR, self.textgrid_fn)
        labels_in = 'he was never identified or captured'.split()
        level = 'Word'
        segInter(fn, labels_in, level)
        self.assert_sc_inter_ok(fn, level, labels_in)

    def test_segInterDir(self):
        transDict = {
            tg_ready_for_inter(FSTEM_1): "I'm sending you on a dangerous mission",
            tg_ready_for_inter(FSTEM_2): "noone else could claim that",
            tg_ready_for_inter(FSTEM_3): "he was never identified or captured"
        }
        level = 'Word'
        segInterDir(PRIV_DIR, transDict, level)
        for k,v in transDict.items():
            fn = os.path.join(PRIV_DIR, f'{k}.TextGrid')
            labels_in = v.split()
            self.assert_sc_inter_ok(fn, level, labels_in)

    def assert_sc_inter_ok(self, fn, level, labels_in):
        s = SpeechCluster(fn)
        tier = s.getTierByName(level)
        labels_out = [seg.label for seg in s.getTierByName(level)]
        labels_in2 = ['sil']
        labels_in2.extend(labels_in)
        labels_in2.append('sil')
        self.assertEqual(labels_in2, labels_out)

def tg_ready_for_inter(fstem, tg=False):
    stem = f'{fstem}_ready_for_inter'
    if tg:
        stem = f'{stem}.TextGrid'
    return stem

if __name__ == '__main__':
    unittest.main()
