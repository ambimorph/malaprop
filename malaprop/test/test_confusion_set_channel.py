# test_confusion_set_channel.py

from malaprop.error_insertion.confusion_set_channel import *
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

def mock_confusion_set(word):

    if word == 'and': return ['an', 'man', 'band']
    return []

class ConfusionSetChannelTest(unittest.TestCase):

    def test_no_error(self):

        output_string = StringIO.StringIO()
        csc = ConfusionSetChannel(MockRNG(gen([0.6]), gen([])), 0.5, mock_confusion_set, output_string.write)
        csc.accept_string('and')
        self.assertEqual(output_string.getvalue(), 'and'), output_string.getvalue()
        self.assertEqual(csc.tokens, 1), csc.tokens
        self.assertEqual(csc.errors, 0), csc.errors

    def test_error(self):

        output_string = StringIO.StringIO()
        csc = ConfusionSetChannel(MockRNG(gen([0.4]), gen([0])), 0.5, mock_confusion_set, output_string.write)
        csc.accept_string('and')
        self.assertEqual(output_string.getvalue(), 'an'), output_string.getvalue()
        self.assertEqual(csc.tokens, 1), csc.tokens
        self.assertEqual(csc.errors, 1), csc.errors

    def test_no_variations(self):

        output_string = StringIO.StringIO()
        csc = ConfusionSetChannel(MockRNG(gen([0.4]), gen([])), 0.5, mock_confusion_set, output_string.write)
        csc.accept_string('man')
        self.assertEqual(output_string.getvalue(), 'man'), output_string.getvalue()
        self.assertEqual(csc.tokens, 1), csc.tokens
        self.assertEqual(csc.errors, 0), csc.errors

