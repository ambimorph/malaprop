# -*- coding: utf-8 -*-
# test_real_word_error_channel.py

from malaprop.error_insertion import real_word_error_channel
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

class SimpleDamerauLevenshteinChannelTest(unittest.TestCase):

    def setUp(self):

        self.error_probabilities = real_word_error_channel.ErrorProbabilities(.2,.2,.2,.2,.2)

    def test_no_error(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.1]), gen([])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_char('a')
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), 'a'), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':1, 'subs':0, 'ins':0, 'dels':0, 'trans':0}), sdlc.stats

    def test_substitution(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.3]), gen([1])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_char('a')
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), 'c'), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':1, 'subs':1, 'ins':0, 'dels':0, 'trans':0}), sdlc.stats

    def test_insertion(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.5,.5]), gen([1,2])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_char(None)
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), 'b'), output_string.getvalue()
        sdlc.accept_char('a')
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), 'bca'), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':1, 'subs':0, 'ins':2, 'dels':0, 'trans':0}), sdlc.stats

    def test_deletion(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.7]), gen([])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_char('a')
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), ''), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':1, 'subs':0, 'ins':0, 'dels':1, 'trans':0}), sdlc.stats

    def test_transposition(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.9, .1,.9]), gen([])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_char('a')
        sdlc.accept_char('b')
        sdlc.accept_char('c')
        sdlc.flush()
        self.assertEqual(output_string.getvalue(), 'acb'), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':3, 'subs':0, 'ins':0, 'dels':0, 'trans':1}), sdlc.stats

    def test_accept_string(self):

        output_string = StringIO.StringIO()
        sdlc = real_word_error_channel.SimpleDamerauLevenshteinChannel(MockRNG(gen([.9, .1,.9, .1]), gen([])), self.error_probabilities, 'abc', output_string.write)
        sdlc.accept_string('abc')
        self.assertEqual(output_string.getvalue(), 'acb'), output_string.getvalue()
        self.assertDictEqual(sdlc.stats, {'chars':3, 'subs':0, 'ins':0, 'dels':0, 'trans':1}), sdlc.stats
        


if __name__ == '__main__':
    unittest.main()
