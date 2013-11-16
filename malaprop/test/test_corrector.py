# test_corrector.py

from malaprop.correction.corrector import *
from recluse.nltk_based_segmenter_tokeniser import *
from malaprop.correction.HMM import *
from DamerauLevenshteinDerivor.cderivor import Derivor
from BackOffTrigramModel.BackOffTrigramModelPipe import BackOffTMPipe
import unittest, StringIO, subprocess

class MatchCaseTest(unittest.TestCase):

    def test_match_case(self):

        result = match_case('This', 'that')
        self.assertEqual(result, 'That'), result

        result = match_case('this', 'that')
        self.assertEqual(result, 'that'), result

        result = match_case('THIS', 'that')
        self.assertEqual(result, 'THAT'), result

class CorrectorTest(unittest.TestCase):

    def setUp(self):
        training_text_file = open('malaprop/test/data/segmenter_training', 'r')
        segmenter_tokeniser = NLTKBasedSegmenterTokeniser(training_text_file)
        path_to_botmp = subprocess.check_output(['which', 'BackOffTrigramModelPipe']).strip()
        arpa_file_name = 'malaprop/test/data/trigram_model_2K.arpa'
        botmp = BackOffTMPipe(path_to_botmp, arpa_file_name)
        error_rate = 0.3
        d = Derivor('malaprop/test/data/1K_test_real_word_vocab')
        self.c = Corrector(segmenter_tokeniser, d.variations, botmp, error_rate)

    def test_correct(self):

        # Regression tests: these results are consistent with the
        # probabilities of their input, but their passing is not a
        # guarantee of correctness.

        sentence  = 'It is therefore a more specific from of the term reflectivity.'
        result = self.c.correct(sentence)
        expected_result = [[9,0, 'term', 'team']]
        self.assertListEqual(result, expected_result), result
        result = self.c.correct(sentence, output='sentence')
        expected_result = 'It is therefore a more specific from of the team reflectivity.'
        self.assertEqual(result, expected_result), result


        sentence  = 'Most land areas are in in albedo range of 0.1 to 0.4.'
        result = self.c.correct(sentence)
        expected_result = [[2,0, 'areas', 'area'], [4,0, 'in', 'win']]
        self.assertListEqual(result, expected_result), result
        result = self.c.correct(sentence, output='sentence')
        expected_result = 'Most land area are win in albedo range of 0.1 to 0.4.'
        self.assertEqual(result, expected_result), result


if __name__ == '__main__':
    unittest.main()

