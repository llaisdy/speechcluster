import os
import shutil
import unittest

from speechcluster.speechCluster import SpeechCluster
from speechcluster.segFake import fakeLabel_and_write, fakeLabel_and_write_dir


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
        [shutil.copy(os.path.join(DATA_DIR, f'{fstem}.wav'), PRIV_DIR)
         for fstem in FSTEMS]
        self.fstem = FSTEM_1
        self.wav_fn = os.path.join(PRIV_DIR, f'{self.fstem}.wav')
        
    def tearDown(self):
        [os.remove(os.path.join(PRIV_DIR, fn)) for fn in os.listdir(PRIV_DIR)]
        pass

    def test_fakeLabel_and_write(self):
        wavFn = self.wav_fn
        phonData = 'q w e r t y u i o p'.split()
        outFormat = 'TextGrid'
        fakeLabel_and_write(wavFn, phonData, outFormat)
        s1 = SpeechCluster(os.path.join(PRIV_DIR, f'{self.fstem}.TextGrid'))
        s1segs = s1.getTierByName('Phone')
        self.assertEqual(len(s1segs), len(phonData)+2)

    def test_fakeLabel_and_write_dir(self):
        wavDir = PRIV_DIR
        transDict = {
            FSTEM_1: 'q w e r t y u i o p',
            FSTEM_2: 'a s d f g h j k l',
            FSTEM_3: 'z x c v b n m',
        }
        outFormat = 'TextGrid'
        fakeLabel_and_write_dir(wavDir, transDict, outFormat)
        for fstem, phonData in transDict.items():
            s1 = SpeechCluster(os.path.join(PRIV_DIR, f'{fstem}.TextGrid'))
            s1segs = s1.getTierByName('Phone')
            self.assertEqual(len(s1segs), len(phonData.split())+2)

if __name__ == '__main__':
    unittest.main()
