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

def trigram_probability(three_words):

    if three_words == ['<s>', '<s>', 'hit']: return -0.9
    if three_words == ['<s>', '<s>', 'it']: return -0.1
    if three_words == ['<s>', '<s>', 'his']: return -0.3

    if three_words == ['<s>', 'hit', 'was']: return -0.1
    if three_words == ['<s>', 'hit', 'as']: return -2.0
    if three_words == ['<s>', 'it', 'was']: return -0.1
    if three_words == ['<s>', 'it', 'as']: return -2.0
    if three_words == ['<s>', 'his', 'was']: return -0.1
    if three_words == ['<s>', 'his', 'as']: return -2.0

    if three_words == ['hit', 'was', '.']: return -0.1
    if three_words == ['hit', 'as', '.']: return -2.0
    if three_words == ['it', 'was', '.']: return -0.1
    if three_words == ['it', 'as', '.']: return -2.0
    if three_words == ['his', 'was', '.']: return -0.1
    if three_words == ['his', 'as', '.']: return -2.0

    else: return -1.0


class HMMTest(unittest.TestCase):

    def test_viterbi(self):

        sentence = ['hit', 'was', '.']
        error_rate = 0.4

        hmm = HMM(confusion, trigram_probability, error_rate)
        result = hmm.viterbi(sentence)
        expected_result = ['it', 'was', '.']
        self.assertListEqual(result, expected_result), result

        error_rate = 0.2

        hmm = HMM(confusion, trigram_probability, error_rate)
        result = hmm.viterbi(sentence)
        expected_result = ['hit', 'was', '.']
        self.assertListEqual(result, expected_result), result

if __name__ == '__main__':
    unittest.main()
