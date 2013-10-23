# test_real_word_error_inserter.py

from malaprop.error_insertion.damerau_levenshtein_channel import *
from malaprop.error_insertion.real_word_error_inserter import *
import unittest, StringIO

class MockRNG:
    def __init__(self, r_generator, c_generator):
        self.r_generator = r_generator
        self.c_generator = c_generator
    def random(self):
        return self.r_generator.next() 
    def choice(self, l):
        return l[self.c_generator.next()]

def gen(l):
    for x in l: yield x

NONE, SUBS, INS, DEL, TRANS = .1, .3, .5, .7, .9
letters = 'abcdefghijklmnopqrstuvwxyz'

class RealWordErrorInserterTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        training_text_file = open('malaprop/test/data/segmenter_training', 'r')
        self.segmenter_tokeniser = NLTKBasedSegmenterTokeniser(training_text_file)
        self.vocabulary = {'is', 'it', 'as', 'a', 'socialism', 'socialist', 'to', 'for', 'from'}
        self.error_probabilities = ErrorProbabilities(.2,.2,.2,.2,.2)
        self.maxDiff = None

    def test_pass_sentence_through_channel(self):

        error_channel = DamerauLevenshteinChannel(MockRNG(gen([NONE for i in range(100)]), gen([])), self.error_probabilities, letters, None)
        rwei = RealWordErrorInserter(self.segmenter_tokeniser, self.vocabulary, error_channel)

        sentence = u'Accordingly, "libertarian socialism" is sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism).\n'
        expected_result = None
        result = rwei.pass_sentence_through_channel(sentence)
        self.assertIs(result, expected_result), result

        error_sequence = [NONE]*8 + [SUBS, NONE, NONE, SUBS] + [NONE]*100
        error_channel = DamerauLevenshteinChannel(MockRNG(gen(error_sequence), gen([letters.index('t')-1]*100)), self.error_probabilities, letters, None)
        rwei = RealWordErrorInserter(self.segmenter_tokeniser, self.vocabulary, error_channel)
        expected_result = u'Accordingly, "libertarian socialist" it sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism).\n', [[2,0,'socialist','socialism'],[3,0,'it','is']]
        result = rwei.pass_sentence_through_channel(sentence)
        self.assertTupleEqual(result, expected_result), result


    def test_corrupt(self):

        file_dict = {\
        'corrupted' : StringIO.StringIO(),\
        'corrections' : StringIO.StringIO(),\
        'adversarial' : StringIO.StringIO(),\
        'key' : StringIO.StringIO(),\
            }

        sentences = u'Accordingly, "libertarian socialism" is sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism). On the other hand, some use "libertarianism" to refer to individualistic free-market philosophy only, referring to free-market anarchism as "libertarian anarchism." '+"Citizens can oppose a decision ('besluit') made by a public body ('bestuursorgaan') within the administration\nThe Treaty could be considered unpopular in Scotland: Sir George Lockhart of Carnwath, the only member of the Scottish negotiating team against union, noted that `The whole nation appears against the Union' and even Sir John Clerk of Penicuik, an ardent pro-unionist and Union negotiator, observed that the treaty was `contrary to the inclinations of at least three-fourths of the Kingdom'."

        error_sequence = [NONE]*8 + [SUBS, NONE, NONE, SUBS] + [NONE]*41 + [DEL] + [NONE]*1000
        error_channel = DamerauLevenshteinChannel(MockRNG(gen(error_sequence), gen([letters.index('t')-1]*1000)), self.error_probabilities, letters, None)
        rwei = RealWordErrorInserter(self.segmenter_tokeniser, self.vocabulary, error_channel)

        expected_dict = {\
            'corrupted' : u'Accordingly, "libertarian socialist" it sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism).\nOn the other hand, some use "libertarianism" to refer to individualistic free-market philosophy only, referring to free-market anarchism a "libertarian anarchism."\n'+"Citizens can oppose a decision ('besluit') made by a public body ('bestuursorgaan') within the administration\nThe Treaty could be considered unpopular in Scotland: Sir George Lockhart of Carnwath, the only member of the Scottish negotiating team against union, noted that `The whole nation appears against the Union' and even Sir John Clerk of Penicuik, an ardent pro-unionist and Union negotiator, observed that the treaty was `contrary to the inclinations of at least three-fourths of the Kingdom'.\n",\
            'corrections' : '[0, [[2, 0, "socialist", "socialism"], [3, 0, "it", "is"]]]\n[1, [[18, 0, "a", "as"]]]\n',\
            'adversarial' : '["Accordingly, \\"libertarian socialism\\" is sometimes used as a synonym for socialist anarchism, to distinguish it from \\"individualist libertarianism\\" (individualist anarchism).\\n", "Accordingly, \\"libertarian socialist\\" it sometimes used as a synonym for socialist anarchism, to distinguish it from \\"individualist libertarianism\\" (individualist anarchism).\\n"]\n["On the other hand, some use \\"libertarianism\\" to refer to individualistic free-market philosophy only, referring to free-market anarchism a \\"libertarian anarchism.\\"\\n", "On the other hand, some use \\"libertarianism\\" to refer to individualistic free-market philosophy only, referring to free-market anarchism as \\"libertarian anarchism.\\"\\n"]\n',\
            'key' : '01'}

        rwei.corrupt(sentences, file_dict, True, True)

        for k in ['corrupted', 'corrections', 'adversarial', 'key']:
            self.assertEqual(expected_dict[k], file_dict[k].getvalue()), k + file_dict[k].getvalue()

if __name__ == '__main__':
    unittest.main()
