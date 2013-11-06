# test_trigram_based_chooser.py

from malaprop.choosing.trigram_based_chooser import *
from recluse.nltk_based_segmenter_tokeniser import *
from BackOffTrigramModel.BackOffTrigramModelPipe import BackOffTMPipe
import unittest, StringIO, subprocess

class TrigramBasedChooserTest(unittest.TestCase):

    def setUp(self):

        training_text_file = open('malaprop/test/data/segmenter_training', 'r')
        segmenter_tokeniser = NLTKBasedSegmenterTokeniser(training_text_file)
        path_to_botmp = subprocess.check_output(['which', 'BackOffTrigramModelPipe']).strip()
        arpa_file_name = 'malaprop/test/data/trigram_model_2K.arpa'
        botmp = BackOffTMPipe(path_to_botmp, arpa_file_name)
        self.c = TrigramBasedChooser(segmenter_tokeniser, botmp.trigram_probability)

    def test_trigram_based_chooser(self):

        pair = ["It is therefore a more specific form of the term reflectivity.", "It is therefore a more specific from of the term reflectivity."]
        result = self.c.choose(pair)
        self.assertEqual(result, 1), result

if __name__ == '__main__':
    unittest.main()
