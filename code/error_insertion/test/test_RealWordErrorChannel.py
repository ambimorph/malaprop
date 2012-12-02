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

        result = self.real_word_error_channel.create_error_with_probability_p(u'', u'a', 1, random_number_generator=r)
        expected_result = u'va'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result

        result = self.real_word_error_channel.create_error_with_probability_p(u'', u'a', .1, random_number_generator=r)
        expected_result = u'a'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result

        result = self.real_word_error_channel.create_error_with_probability_p(u's', u'a', 1, random_number_generator=r)
        expected_result = u'sta'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result

        result = self.real_word_error_channel.create_error_with_probability_p(u's', u'', 1, random_number_generator=r)
        expected_result = u'st'
        assert result == expected_result, u'Expected ' + expected_result + ', but got ' + result

    def test_pass_token_through_channel(self):

        r = random.Random(999)
        self.real_word_error_channel.real_word_errors = 0
        self.real_word_error_channel.real_word_tokens_passed_though = 0
        self.real_word_error_channel.mean_errors_per_word = 0
        self.real_word_error_channel.max_errors_per_word = 0

        test_tokens = [u'an', u'and', u'the', u'there', u'late', u'"']
        results = []
        for token in test_tokens:
            for i in range(500):
                result = self.real_word_error_channel.pass_token_through_channel(token, random_number_generator=r)
                if result != token:
                    results.append(token + ' ' + str(i) + ' ' + result + ' ' + str(self.real_word_error_channel.real_word_errors) + ' ' + \
                         str(self.real_word_error_channel.real_word_tokens_passed_though) + ' ' + \
                         str(self.real_word_error_channel.mean_errors_per_word) + ' ' + str(self.real_word_error_channel.max_errors_per_word))

        assert results == [ \
                'an 18 man 1 19 1 1', \
                'an 30 any 2 31 1 1', \
                'an 92 up 3 93 1 3', \
                'an 157 ran 4 158 1 3', \
                'an 215 ran 5 216 1 3', \
                'an 217 a 6 218 1 3', \
                'an 219 a 7 220 1 3', \
                'an 220 and 8 221 1 3', \
                'an 251 can 9 252 1 3', \
                'an 252 a 10 253 1 3', \
                'an 260 in 11 261 1 3', \
                'an 299 a 12 300 1 3', \
                'an 327 a 13 328 1 3', \
                'an 329 a 14 330 1 3', \
                'an 330 a 15 331 1 3', \
                'an 365 a 16 366 1 3', \
                'an 378 a 17 379 1 3', \
                'an 391 a 18 392 1 3', \
                'an 393 a 19 394 1 3', \
                'an 401 in 20 402 1 3', \
                'an 409 a 21 410 1 3', \
                'an 423 a 22 424 1 3', \
                'an 440 a 23 441 1 3', \
                'an 448 on 24 449 1 3', \
                'an 473 and 25 474 1 3', \
                'an 498 a 26 499 1 3', \
                'and 42 an 27 543 1 3', \
                'and 100 an 28 601 1 3', \
                'and 125 an 29 626 1 3', \
                'and 126 an 30 627 1 3', \
                'and 191 an 31 692 1 3', \
                'and 200 an 32 701 1 3', \
                'and 244 had 33 745 1 3', \
                'and 289 an 34 790 1 3', \
                'and 297 an 35 798 1 3', \
                'and 302 an 36 803 1 3', \
                'and 319 an 37 820 1 3', \
                'and 331 an 38 832 1 3', \
                'and 362 an 39 863 1 3', \
                'and 365 an 40 866 1 3', \
                'and 456 an 41 957 1 3', \
                'and 463 an 42 964 1 3', \
                'and 480 a 43 981 1 3', \
                'the 47 to 44 1048 1 3', \
                'the 105 t 45 1106 1 3', \
                'the 123 then 46 1124 1 3', \
                'the 275 t 47 1276 1 3', \
                'the 430 get 48 1431 1 3', \
                'the 497 she 49 1498 1 3', \
                'there 112 three 50 1613 1 3', \
                'there 128 three 51 1629 1 3', \
                'there 133 three 52 1634 1 3', \
                'there 166 three 53 1667 1 3', \
                'there 176 three 54 1677 1 3', \
                'there 223 three 55 1724 1 3', \
                'there 245 three 56 1746 1 3', \
                'there 258 three 57 1759 1 3', \
                'there 272 three 58 1773 1 3', \
                'there 274 three 59 1775 1 3', \
                'there 283 where 60 1784 1 3', \
                'there 305 three 61 1806 1 3', \
                'there 309 three 62 1810 1 3', \
                'there 319 three 63 1820 1 3', \
                'there 325 them 64 1826 1 3', \
                'there 343 three 65 1844 1 3', \
                'there 352 three 66 1853 1 3', \
                'there 355 the 67 1856 1 3', \
                'there 495 then 68 1996 1 3', \
                'late 142 date 69 2143 1 3', \
                'late 247 lake 70 2248 1 3', \
                'late 386 later 71 2387 1 3', \
            ]
            



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
