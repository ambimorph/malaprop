# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_RealWordErrorChannel.py

import NLTKSegmentThenTokenise, RealWordErrorChannel
import unittest, random, StringIO


class RealWordErrorChannelTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        text_to_corrupt = open('test_data/text_to_corrupt', 'rb')
        vocab_file = open('test_data/1K_test_vocab', 'rb')
        corrupted = open('/tmp/test_error_corpus', 'wb')
        p = .3
        self.real_word_error_channel = RealWordErrorChannel.RealWordErrorChannel(text_to_corrupt, vocab_file, corrupted, p, None)

    def test_real_words(self):
        for test_word in [u'with', u'end.of.document', u'don\'t']:
            assert self.real_word_error_channel.is_real_word(test_word), test_word
        for test_word in [u'xxxx', u'-', u'.', u'<3-digit-integer>']:
            assert not self.real_word_error_channel.is_real_word(test_word), test_word

    def test_symbols(self):
        for test_symbol in [u'x', u'\'']:
            assert test_symbol in self.real_word_error_channel.symbols, test_symbol
        for test_symbol in [u'β']:
            assert test_symbol not in self.real_word_error_channel.symbols, test_symbol

    def test_create_error_with_probability_p(self):
        r = random.Random(999)

        result, error_was_created = self.real_word_error_channel.create_error_with_probability_p(u'', u'a', 1, random_number_generator=r)
        expected_result = u'va'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result
        assert error_was_created == True, u'Expected True, got ' + str(error_was_created)

        result, error_was_created = self.real_word_error_channel.create_error_with_probability_p(u'', u'a', .1, random_number_generator=r)
        expected_result = u'a'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result
        assert error_was_created == False, u'Expected False, got ' + str(error_was_created)

        result, error_was_created = self.real_word_error_channel.create_error_with_probability_p(u's', u'a', 1, random_number_generator=r)
        expected_result = u'sta'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result
        assert error_was_created == True, u'Expected True, got ' + str(error_was_created)

        result, error_was_created = self.real_word_error_channel.create_error_with_probability_p(u's', u'', 1, random_number_generator=r)
        expected_result = u'st'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result
        assert error_was_created == True, u'Expected True, got ' + str(error_was_created)

    def test_pass_token_through_channel(self):

        r = random.Random(999)

        test_cases = [ \
            (u'a', u'xxx', 100, 100, 100, 100), \
            (u'and', u'xxx', 100, 100, 100, 100), \
            (u'"', u'"', 100, 100, 100, 100), \
                ]

        for test_case in test_cases:

            result = self.real_word_error_channel.pass_token_through_channel(test_case[0], random_number_generator=r)
            expected_result = test_case[1]
            assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result
            assert self.real_word_error_channel.real_word_errors == test_case[2]
            assert self.real_word_error_channel.real_word_tokens_passed_though == test_case[3]
            assert self.real_word_error_channel.mean_errors_per_word == test_case[4]
            assert self.real_word_error_channel.max_errors_per_word == test_case[5]


    def test_pass_sentence_through_channel(self):
        r = random.Random(999)
        sentence_and_token_information = \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 32, 33, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, u'<4-digit-integer>')])
        out_file_obj = StringIO.StringIO()
        self.real_word_error_channel.pass_sentence_through_channel(sentence_and_token_information, random_number_generator=r)
        expected_text_output = u'xxxxxxxxxxxx'
        assert isinstance(out_file_obj.getvalue(), str), (type(out_file_obj.getvalue()), repr(out_file_obj.getvalue()))
        try:
            assert out_file_obj.getvalue() == expected_text_output
        except AssertionError, exp:
            i = 0
            x = out_file_obj.getvalue()
            for i in range(len(x)):
                if i >= len(expected_text_output) or x[i] != expected_text_output[i]: break
            print '\nMatching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_text_output[i:])
            raise exp

    def test_pass_file_through_channel(self):
        r = random.Random(999)
        text_to_create_errors_in = u'Another libertarian tradition is that of unschooling and the free school in which child-led activity replaces pedagogic approaches. Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921. Summerhill is often cited as an example of anarchism in practice. However, although Summerhill and other free schools are radically libertarian, they differ in principle from those of Ferrer by not advocating an overtly-political class struggle-approach.\nThe Academy of Motion Picture Arts and Sciences itself was conceived by Metro-Goldwyn-Mayer studio boss Louis B. Mayer.  The 1st Academy Awards ceremony was held on Thursday, May 16, 1929, at the Hotel Roosevelt in Hollywood to honor outstanding film achievements of 1927 and 1928.\nWhen the Western Roman Empire collapsed, Berbers became independent again in many areas, while the Vandals took control over other parts, where they remained until expelled by the generals of the Byzantine Emperor, Justinian I. The Byzantine Empire then retained a precarious grip on the east of the country until the coming of the Arabs in the eighth century.'
        expected_text_output = u'xxx'
        expected_error_rate = .6
        expected_mean_errors_per_word = 1000
        expected_max_errors_per_word = 1000

        error_rate, mean_errors_per_word, max_errors_per_word = self.real_word_error_channel.pass_file_through_channel(text=text_to_create_errors_in, random_number_generator=r)
        assert error_rate == expected_error_rate, "Expected error_rate " + str(expected_error_rate) + ", but got " + str(error_rate)
        assert mean_errors_per_word == expected_mean_errors_per_word, "Expected mean_errors_per_word " + str(expected_mean_errors_per_word) + ", but got " + str(mean_errors_per_word)
        assert max_errors_per_word == expected_max_errors_per_word, "Expected max_errors_per_word-rate " + str(expected_max_errors_per_word) + ", but got " + str(max_errors_per_word)
        
        assert isinstance(out_file_obj.getvalue(), str), (type(out_file_obj.getvalue()), repr(out_file_obj.getvalue()))
        try:
            assert out_file_obj.getvalue() == expected_text_output
        except AssertionError, exp:
            x = out_file_obj.getvalue()
            for i in range(len(x)):
                if i >= len(expected_text_output) or x[i] != expected_text_output[i]: break
            print '\nMatching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_text_output[i:])
            raise exp
        
if __name__ == '__main__':
    unittest.main()
