# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_RealWordErrorChannel.py

from recluse import nltk_based_segmenter_tokeniser
from malaprop.error_insertion import RealWordErrorChannel
import unittest, random, StringIO

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

class RealWordErrorChannelTest(unittest.TestCase):
    
    def setUp(self):
        self.text_to_corrupt = open('malaprop/test/data/segmenter_training', 'rb')
        self.vocab_file = open('malaprop/test/data/1K_test_real_word_vocab', 'rb')
        self.corrupted_file = StringIO.StringIO()
        self.corrections_file = StringIO.StringIO()
        self.p = .3
        self.r = random.Random(999)
        class MockSegmenterTokenizer:
            def __init__(self, *args, **kwargs):
                pass

        self.original_segmenter_tokeniser = nltk_based_segmenter_tokeniser.NLTKBasedSegmenterTokeniser
        nltk_based_segmenter_tokeniser.NLTKBasedSegmenterTokeniser = MockSegmenterTokenizer

        self.real_word_error_channel = RealWordErrorChannel.RealWordErrorChannel(self.vocab_file, self.corrupted_file, self.corrections_file, self.p, self.r)

    def tearDown(self):
        
        nltk_based_segmenter_tokeniser.NLTKBasedSegmenterTokeniser = self.original_segmenter_tokeniser 

    def test_real_words(self):
        for test_word in [u'with', u'end', u'don\'t']:
            assert self.real_word_error_channel.is_real_word(test_word), test_word
        for test_word in [u'xxxx', u'-', u'.', u'<3-digit-integer>', u'end.of.document']:
            assert not self.real_word_error_channel.is_real_word(test_word), test_word

    def test_symbols(self):
        for test_symbol in [u'x', u'\'']:
            assert test_symbol in self.real_word_error_channel.symbols, test_symbol
        for test_symbol in [u'β']:
            assert test_symbol not in self.real_word_error_channel.symbols, test_symbol

    def test_create_error(self):

        test_cases = [(u'', u'a'), (u's', u'a'), (u's', u'')]
        # no error, insertion, deletion, substitution, transposition
        mock_random_arguments = [([1],[0]), ([0],[0,0]), ([0],[1]), ([0],[2,2]), ([0],[3])]
        expected_results = { (0,0):[u'', u'a'], \
                             (0,1):[u'', u"'", u'a'], \
                             (0,2):[u''], \
                             (0,3):[u'', u"c"], \
                             (1,0):[u's', u'a'], \
                             (1,1):[u's', u"'", u'a'], \
                             (1,2):[u's'], \
                             (1,3):[u's', u'c'], \
                             (1,4):[u'a', u's'], \
                             (2,0):[u's', u''], \
                             (2,1):[u's', u"'", u'']}

        for k,v in expected_results.iteritems():
            mock_random_generator = [map(gen, x) for x in [i for i in mock_random_arguments]]
            self.real_word_error_channel.random_number_generator = MockRNG(*(mock_random_generator[k[1]]))
        
            try:
                result = self.real_word_error_channel.create_error(*test_cases[k[0]])
                assert result == v
 
            except AssertionError, exp:
                print k, test_cases[k[0]], mock_random_arguments[k[1]]
                print  u'Expected ' + str(v) + ', but got ' + str(result)
                raise exp

    def test_create_all_possible_errors_and_probs(self):

        test_cases = [ \
            (u'', u'a', \
                 [(s + u'a', 1.0/3*1.0/(len(self.real_word_error_channel.symbols))) for s in self.real_word_error_channel.symbols] + \
                 [(u'', 1.0/3)] + \
                 [(s, 1.0/3*1.0/(len(self.real_word_error_channel.symbols)-1)) for s in self.real_word_error_channel.symbols[:self.real_word_error_channel.symbols.index(u'a')] + self.real_word_error_channel.symbols[self.real_word_error_channel.symbols.index(u'a')+1:]]), \
            (u's', u'a', \
                 [(u's' + s + u'a', 1.0/4*1.0/(len(self.real_word_error_channel.symbols))) for s in self.real_word_error_channel.symbols] + \
                 [(u's', 1.0/4)] + \
                 [(u's' + s, 1.0/4*1.0/(len(self.real_word_error_channel.symbols)-1)) for s in self.real_word_error_channel.symbols[:self.real_word_error_channel.symbols.index(u'a')] + self.real_word_error_channel.symbols[self.real_word_error_channel.symbols.index(u'a')+1:]] + \
                 [(u'as', 1.0/4)]), \
            (u's', u'', \
                 [(u's' + s, 1.0/(len(self.real_word_error_channel.symbols))) for s in self.real_word_error_channel.symbols])]

        for t in test_cases:
            try:
                result = self.real_word_error_channel.create_all_possible_errors_and_probs(t[0], t[1])
                assert result == t[2]
 
            except AssertionError, exp:
                print  u'Expected ' + repr(t[2]) + ', but got ' + repr(result)
                raise exp

    def test_mct_eq(self):
        mct0 = RealWordErrorChannel.MidChannelToken(u'and')
        mct0base = RealWordErrorChannel.MidChannelToken(u'and')

        assert mct0 == mct0base
        
        mct1 = RealWordErrorChannel.MidChannelToken(u'xnd')

        assert mct0 != mct1

    def test_push_one_char_does_not_mutate_token(self):

        self.real_word_error_channel.random_number_generator = MockRNG(gen([1]),gen([0]))
        mct0 = RealWordErrorChannel.MidChannelToken(u'and')
        mct1 = self.real_word_error_channel.push_one_char(mct0)
        mct0base = RealWordErrorChannel.MidChannelToken(u'and')
        assert mct0 == mct0base, (repr(mct0), repr(mct0base))

    def test_push_one_char_no_error(self):
        
        # create no error
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,1,1,1]),gen([0]))

        attributes = ['chars_passed',
            'left_char',
            'right_char',
            'remaining_chars',
            'number_of_errors']

        mct0 = RealWordErrorChannel.MidChannelToken(u'and')
        mct1 = self.real_word_error_channel.push_one_char(mct0)
        expected_attributes = (u'', u'a', u'n', [u'd', u''], 0)
        for i in range(len(attributes)):
            self.assertEqual(getattr(mct1, attributes[i]), expected_attributes[i])

        mct2 = self.real_word_error_channel.push_one_char(mct1)
        expected_attributes = (u'a', u'n', u'd', [u''], 0)
        
        mct3 = self.real_word_error_channel.push_one_char(mct2)
        expected_attributes = (u'an', u'd', u'', [], 0)

        mct4 = self.real_word_error_channel.push_one_char(mct3)
        expected_attributes = (u'and', u'', u'', [], 0)

        try:
            mct5 = self.real_word_error_channel.push_one_char(mct4)
        except:
            pass
        else:
            self.assertRaises(AssertionError)
        
    def test_push_one_char_error(self):
        
        attributes = ['chars_passed',
            'left_char',
            'right_char',
            'remaining_chars',
            'number_of_errors']

        mct0 = RealWordErrorChannel.MidChannelToken(u'ask')
        expected_attributes = (u'', u'', u'a', [u's', u'k', u''], 0)
        for i in range(len(attributes)):
            self.assertEqual(getattr(mct0, attributes[i]), expected_attributes[i])
        # insertion, deletion, substitution, transposition
        mock_random_arguments = [([0],[0,0]), ([0],[1]), ([0],[2,2]), ([0],[3])]
        mock_random_generator = [map(gen, x) for x in [i for i in mock_random_arguments]]
        expected_attributes = [(u'\'', u'a', u's', [u'k', u''], 1),
                               (u'', u'', u's', [u'k', u''], 1),
                               (u'c', u'', u's', [u'k', u''], 1)]

        for i in [2, 1, 0]: # to end on token with 2 chars in channel for next part
            self.real_word_error_channel.random_number_generator = MockRNG(*mock_random_generator[i])
            mct1 = self.real_word_error_channel.push_one_char(mct0)
            for j in range(len(attributes)):
                self.assertEqual(getattr(mct1, attributes[j]), expected_attributes[i][j], repr(mct1))

        # mct1 now = <MidChannelToken u"'" u'a' u's' [u'k', u''] 1 0>
        expected_attributes = [(u"'a'", u's', u'k', [u''], 2),
                               (u"'a", u'', u'k', [u''], 2),
                               (u"'aa", u'', u'k', [u''], 2),
                               (u"'sa", u'', u'k', [u''], 2)]

        mock_random_generator = [map(gen, x) for x in [i for i in mock_random_arguments]]
        for i in range(4):
            self.real_word_error_channel.random_number_generator = MockRNG(*mock_random_generator[i])
            mct2 = self.real_word_error_channel.push_one_char(mct1)
            for j in range(len(attributes)):
                self.assertEqual(getattr(mct2, attributes[j]), expected_attributes[i][j], repr(mct2))

        
    def test_pass_token_through_channel(self):

        self.real_word_error_channel.reset_stats()

        token_0 = u'an'
        token_1 = u'man'
        token_2 = u'then'
        token_3 = u'ten'
        token_4 = u'no'

        # No error
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,1,1]),gen([0]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, token_0)

        # error that gets corrected, because it is not a real word: man -> mn
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0,1,1]), gen([1]))
        result = self.real_word_error_channel.pass_token_through_channel(token_1)
        self.assertEqual(result, u'man')

        # deletion at the beginning: man -> an
        self.real_word_error_channel.random_number_generator = MockRNG(gen([0,1,1,1]), gen([1]))
        result = self.real_word_error_channel.pass_token_through_channel(token_1)
        self.assertEqual(result, u'an')

        # deletion in the middle: then -> ten
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0,1,1,1]), gen([1]))
        result = self.real_word_error_channel.pass_token_through_channel(token_2)
        self.assertEqual(result, u'ten')

        # deletion at end: an -> a
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0]),gen([1]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, u'a')
        
        # insertion at beginning: an -> man
        m = self.real_word_error_channel.symbols.index(u'm')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([0,1,1]),gen([0,m]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, u'man')

        # insertion in the middle: ten -> then
        h = self.real_word_error_channel.symbols.index(u'h')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0,1,1]),gen([0,h]))
        result = self.real_word_error_channel.pass_token_through_channel(token_3)
        self.assertEqual(result, u'then')

        # insertion at end: an -> and
        d = self.real_word_error_channel.symbols.index(u'd')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,1,0]),gen([d]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, u'and')

        # substitution at beginning: an -> in
        a = self.real_word_error_channel.symbols.index(u'a')
        symbols_minus_a = self.real_word_error_channel.symbols[:a] + \
            self.real_word_error_channel.symbols[a+1:]
        i = symbols_minus_a.index(u'i')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([0,1,1]),gen([2,i]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, u'in')

        # substitution in the middle: then -> than
        e = self.real_word_error_channel.symbols.index(u'e')
        symbols_minus_e = self.real_word_error_channel.symbols[:e] + \
            self.real_word_error_channel.symbols[e+1:]
        a = symbols_minus_e.index(u'a')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,1,0,1,1]),gen([2,a]))
        result = self.real_word_error_channel.pass_token_through_channel(token_2)
        self.assertEqual(result, u'than')

        # substitution at end: an -> as
        n = self.real_word_error_channel.symbols.index(u'n')
        symbols_minus_n = self.real_word_error_channel.symbols[:n] + \
            self.real_word_error_channel.symbols[n+1:]
        s = symbols_minus_n.index(u's')
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0]),gen([2,s]))
        result = self.real_word_error_channel.pass_token_through_channel(token_0)
        self.assertEqual(result, u'as')

        # transposition: no -> on
        self.real_word_error_channel.random_number_generator = MockRNG(gen([1,0]),gen([3]))
        result = self.real_word_error_channel.pass_token_through_channel(token_4)
        self.assertEqual(result, u'on')


    def test_pass_sentence_through_channel(self):

        def mock_pass_token_through_channel(token):
            if token == u'led':
                return u'lead'
            elif token == u'Overt':
                return u'Over'
            return token

        self.real_word_error_channel.reset_stats()
        sentences = [ \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 32, 33, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, u'<4-digit-integer>')]), \
            (u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', \
            [5, 6, 14, 15, 24, 25, 30, 31, 36, 37, 40, 41, 44, 45, 47, 48, 51, 52, 58, 59, 60, 66, 67, 78, 79, 81, 82, 85, 86, 89, 90, 92, 93, 98, 99, 104, 105, 106, 109, 110, 114, 115, 117, 118, 126, 127, 134, 135, 144, 145, 146, 154, 155, 160, 161, 163, 164, 168, 169, 174, 175, 179], [])]

        original_pass_token_through_channel = self.real_word_error_channel.pass_token_through_channel
        self.real_word_error_channel.pass_token_through_channel = mock_pass_token_through_channel
        result, corrections = self.real_word_error_channel.pass_sentence_through_channel(sentences[0])
        self.assertEqual(result, u'Experiments in Germany lead to A. S. Neill founding what became Summerhill School in 1921.')
        self.assertEqual(corrections, [(23, u'lead', u'led')])

        result, corrections = self.real_word_error_channel.pass_sentence_through_channel(sentences[1])
        self.assertEqual(result, u'Over symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.')
        self.assertEqual(corrections, [(0, u'Over', u'Overt')])

        self.real_word_error_channel.pass_token_through_channel = original_pass_token_through_channel

    def test_pass_sentence_through_channel_regression(self):
        self.real_word_error_channel.random_number_generator = random.Random(79)
        sentences = [ \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 32, 33, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, u'<4-digit-integer>')]), \
            (u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', \
            [5, 6, 14, 15, 24, 25, 30, 31, 36, 37, 40, 41, 44, 45, 47, 48, 51, 52, 58, 59, 60, 66, 67, 78, 79, 81, 82, 85, 86, 89, 90, 92, 93, 98, 99, 104, 105, 106, 109, 110, 114, 115, 117, 118, 126, 127, 134, 135, 144, 145, 146, 154, 155, 160, 161, 163, 164, 168, 169, 174, 175, 179], [])]

        expected_results = [[\
                (5, u'Experiments in Germany led too A. S. Neill founding what became Summerhill School in 1921.', [(27, u'too', u'to')]),
                (6, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School in 1921.', [(27, u't', u'to')]),
                (9, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]),
                (15, u'Experiments c Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'c', u'in')]),
                (21, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]),
                (25, u'Experiments one Germany led got A. S. Neill founding what became Summerhill School in 1921.', [(12, u'one', u'in'), (27, u'got', u'to')]),
                (27, u'Experiments c Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'c', u'in')]),
                (30, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School in 1921.', [(27, u't', u'to')]),
                (47, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]),
                (56, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School i 1921.', [(81, u'i', u'in')]),
                (57, u'Experiments win Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'win', u'in')]),
                (60, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]),
                (69, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School in 1921.', [(27, u't', u'to')]),
                (73, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School i 1921.', [(27, u't', u'to'), (81, u'i', u'in')])
                     ], [\
                (1, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend on continue through adulthood, although often in more muted form.', [(115, u'on', u'to')]),
                (2, u'Overt symptoms gradually begin after he age of six months, become established by age i or three years, and tend to continue through adulthood, although often in more muted form.', [(37, u'he', u'the'), (86, u'i', u'two')]),
                (3, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.', [(79, u'b', u'by')]),
                (4, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often is more muted form.', [(161, u'is', u'in')]),
                (9, u'Overt symptoms gradually begin after the age m six months, become established by age two or three years, and tend to continue through adulthood, although often in are muted form.', [(45, u'm', u'of'), (164, u'are', u'more')]),
                (10, u'Overt symptoms gradually begin after the age of six months, come established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(60, u'come', u'become')]),
                (14, u'Overt symptoms gradually begin after he age of six months, become established by age two or they years, and tend t continue through adulthood, although often in more muted form.', [(37, u'he', u'the'), (93, u'they', u'three'), (115, u't', u'to')]),
                (15, u'Overt symptoms gradually begin after the a of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.', [(41, u'a', u'age'), (161, u'i', u'in')]),
                (18, u'Overt symptoms gradually begin after the age of six months, become established by age two or three year, and tend to continue through adulthood, although often i more muted form.', [(99, u'year', u'years'), (161, u'i', u'in')]),
                (24, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted for.', [(175, u'for', u'form')]),
                (26, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, end tend to continue through adulthood, although often in more muted form.', [(106, u'end', u'and')]),
                (33, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often x more muted form.', [(79, u'b', u'by'), (161, u'x', u'in')]) ,
                (34, u'Overt symptoms gradually begin after her age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(37, u'her', u'the')]) ,
                (35, u'Overt symptoms gradually begin after the age of six months, become established by age t or there years, and tend to continue through adulthood, although often in more muted form.', [(86, u't', u'two'), (93, u'there', u'three')]),
                (43, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.', [(86, u'to', u'two')]),
                (46, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.', [(106, u'an', u'and')]),
                (48, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.', [(79, u'b', u'by')]),
                (50, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend x continue through adulthood, although often in or muted form.', [(115, u'x', u'to'), (164, u'or', u'more')]),
                (54, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend b continue through adulthood, although often in more muted form.', [(115, u'b', u'to')]),
                (57, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.', [(161, u'i', u'in')]),
                (58, u'Overt symptoms gradually begin after the a of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(41, u'a', u'age')]),
                (59, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.', [(79, u'b', u'by')]),
                (61, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, an tend to continue through adulthood, although often in more muted form.', [(86, u'to', u'two'), (106, u'an', u'and')]),
                (63, u'Overt symptoms gradually begin after the age of six months, become established by age two or the years, and tend to continue through adulthood, although often if more muted form.', [(93, u'the', u'three'), (161, u'if', u'in')]),
                (64, u'Overt symptoms gradually begin after he age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(37, u'he', u'the')]),
                (65, u'Overt symptoms gradually begin after them age of six months, become established b age two or three years, and tend to continue through adulthood, although often i more muted form.', [(37, u'them', u'the'), (79, u'b', u'by'), (161, u'i', u'in')]),
                (66, u'Overt symptoms gradually begin after the a of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(41, u'a', u'age')]),
                (67, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.', [(115, u't', u'to')]),
                (69, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.', [(106, u'an', u'and')]),
                (72, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.', [(161, u'i', u'in')]),
                (73, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, a tend to continue through adulthood, although often in more muted form.', [(106, u'a', u'and')]),
                (74, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.', [(86, u'to', u'two')]),
                (75, u'Overt symptoms gradually begin after the age of six months, become established by age two or three year, and tend to continue through adulthood, although often in more muted form.', [(99, u'year', u'years')]),
                (78, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted forms.', [(175, u'forms', u'form')]),
                (79, u'Overt symptoms gradually begin after the age of six months, become established by de two or three years, an tend to continue through adulthood, although often in more muted form.', [(82, u'de', u'age'), (106, u'an', u'and')])
                     ]]
                                
        for i in range(len(sentences)):
            sentence_and_token_information = sentences[i]
            expected = expected_results[i]
            results = []
            for i in range(80):
                result, corrections = self.real_word_error_channel.pass_sentence_through_channel(sentence_and_token_information)
                if result != sentence_and_token_information[0]:
                    results.append((i, result, corrections))

            try:
                assert len(results) == len(expected), str(len(results)) + ' ' + str(len(expected))
                assert repr(results) == repr(expected), '\n' + repr(results) + '\n\n\n' + repr(expected)
            except AssertionError, exp:
                print sentence_and_token_information[0]
                for res in results: print res
                for i in range(len(results)):
                    if results[i] == expected[i]:
                        print '\nMatched: ', results[i]
                    else:
                        print '\nDid not match: \nGot: ', results[i], '\nExpected: ', expected[i]
                raise exp

