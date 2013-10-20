# -*- coding: utf-8 -*-
# test_damerau_levenshtein_channel.py

from malaprop.error_insertion import damerau_levenshtein_channel
import unittest, StringIO

def gen(l):
    for x in l: yield x

class MockRNG:
    def __init__(self, r_generator, c_generator):
        self.r_generator = r_generator
        self.c_generator = c_generator
    def random(self):
        return self.r_generator.next() 
    def choice(self, l):
        return l[self.c_generator.next()]

class DamerauLevenshteinChannelTest(unittest.TestCase):

    def setUp(self):

        self.error_probabilities = damerau_levenshtein_channel.ErrorProbabilities(.2,.2,.2,.2,.2)

    def test_unknown_char(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.3]), gen([1])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char('x')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'x'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':0, 'subs':0, 'ins':0, 'dels':0, 'trans':0}), dlc.stats

    def test_no_error(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.1]), gen([])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char('a')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'a'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':1, 'subs':0, 'ins':0, 'dels':0, 'trans':0}), dlc.stats

    def test_substitution(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.3]), gen([1])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char('a')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'c'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':1, 'subs':1, 'ins':0, 'dels':0, 'trans':0}), dlc.stats

    def test_insertion(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.5,.5]), gen([1,2])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char(None)
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'b'), output_string.getvalue()
        dlc.accept_char('a')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'bca'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':1, 'subs':0, 'ins':2, 'dels':0, 'trans':0}), dlc.stats

    def test_deletion(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.7]), gen([])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char('a')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), ''), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':1, 'subs':0, 'ins':0, 'dels':1, 'trans':0}), dlc.stats

    def test_transposition(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.9, .1,.9]), gen([])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_char('a')
        dlc.accept_char('b')
        dlc.accept_char('c')
        dlc.flush()
        self.assertEqual(output_string.getvalue(), 'acb'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':3, 'subs':0, 'ins':0, 'dels':0, 'trans':1}), dlc.stats

    def test_accept_string(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.9, .1,.9, .1]), gen([])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_string('abc')
        self.assertEqual(output_string.getvalue(), 'acb'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':3, 'subs':0, 'ins':0, 'dels':0, 'trans':1}), dlc.stats
        
    def test_accept_string_with_unknown_chars(self):

        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.1, .9, .1, .1]), gen([])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_string('\'bc')
        self.assertEqual(output_string.getvalue(), '\'bc'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':2, 'subs':0, 'ins':0, 'dels':0, 'trans':0}), dlc.stats
        
        output_string = StringIO.StringIO()
        dlc = damerau_levenshtein_channel.DamerauLevenshteinChannel(MockRNG(gen([.1, .1, .1, .5, .9, .1,.9, .1]), gen([0])), self.error_probabilities, 'abc', output_string.write)
        dlc.accept_string('aaa\'bc')
        self.assertEqual(output_string.getvalue(), 'aaaa\'bc'), output_string.getvalue()
        self.assertDictEqual(dlc.stats, {'chars':5, 'subs':0, 'ins':1, 'dels':0, 'trans':0}), dlc.stats
        


if __name__ == '__main__':
    unittest.main()
