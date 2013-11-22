# test_HMM.py

from malaprop.correction.HMM import *
import unittest, StringIO

def confusion(word):

    if word == 'hit': return ['it', 'his']
    if word == 'it': return ['hit', 'is']
    if word == 'his': return ['is', 'hit']

    if word == 'was': return ['as']
    if word == 'as': return ['was', 'a']

    return []

class MockTrigramModelPipe():

    def trigram_probability(self, three_words):

        if three_words == ('<s>', '<s>', 'hit'): return -0.9
        if three_words == ('<s>', '<s>', 'it'): return -0.1
        if three_words == ('<s>', '<s>', 'his'): return -1.9
        
        if three_words == ('<s>', 'hit', 'was'): return -0.1
        if three_words == ('<s>', 'hit', 'as'): return -2.0
        if three_words == ('<s>', 'it', 'was'): return -0.1
        if three_words == ('<s>', 'it', 'as'): return -2.0
        if three_words == ('<s>', 'his', 'was'): return -0.1
        if three_words == ('<s>', 'his', 'as'): return -0.0
        
        if three_words == ('hit', 'was', '.'): return -3.1
        if three_words == ('hit', 'as', '.'): return -5.0
        if three_words == ('it', 'was', '.'): return -3.1
        if three_words == ('it', 'as', '.'): return -5.0
        if three_words == ('his', 'was', '.'): return -3.1
        if three_words == ('his', 'as', '.'): return -0.0
        
        else: return -1.0

    def in_bigrams(self, bigram):
        return True

    def bigram_backoff(self, bigram):
        return 0

    def unigram_backoff(self, bigram):
        return 0

class HMMTest(unittest.TestCase):

    

    def test_viterbi_two(self):

        sentence = ['hit', 'was', '.']
        mock_tmp = MockTrigramModelPipe()

        error_rate = 0.4
        hmm = HMM(confusion, mock_tmp, error_rate, 2)
        result = hmm.viterbi(sentence)
        expected_result = ('his', 'as', '.')
        self.assertTupleEqual(result, expected_result), result

        hmm = HMM(confusion, mock_tmp, error_rate, 2, surprise_index=3)
        result = hmm.viterbi(sentence)
        expected_result = ('it', 'was', '.')
        self.assertTupleEqual(result, expected_result), result

        hmm = HMM(confusion, mock_tmp, error_rate, 2, surprise_index=9)
        result = hmm.viterbi(sentence)
        expected_result = ('hit', 'was', '.')
        self.assertTupleEqual(result, expected_result), result

        error_rate = 0.1
        hmm = HMM(confusion, mock_tmp, error_rate, 2)
        result = hmm.viterbi(sentence)
        expected_result = ('hit', 'was', '.')
        self.assertTupleEqual(result, expected_result), result

    def test_viterbi_three(self):

        sentence = ['hit', 'was', '.']
        mock_tmp = MockTrigramModelPipe()

        error_rate = 0.4
        hmm = HMM(confusion, mock_tmp, error_rate, 3, prune_to=100)
        result = hmm.viterbi(sentence)
        expected_result = ('his', 'as', '.')
        self.assertTupleEqual(result, expected_result), result

        hmm = HMM(confusion, mock_tmp, error_rate, 3, prune_to=1)
        result = hmm.viterbi(sentence)
        expected_result = ('it', 'was', '.')
        self.assertTupleEqual(result, expected_result), result


if __name__ == '__main__':
    unittest.main()

