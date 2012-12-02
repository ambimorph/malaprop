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
        self.real_word_error_channel.reset_stats()

        test_tokens = [u'an', u'and', u'the', u'there', u'late', u'"']
        results = []
        for token in test_tokens:
            for i in range(500):
                result = self.real_word_error_channel.pass_token_through_channel(token, random_number_generator=r)
                if result != token:
                    results.append(token + ' ' + str(i) + ' ' + result + ' ' + str(self.real_word_error_channel.real_word_errors) + ' ' + \
                         str(self.real_word_error_channel.real_word_tokens_passed_though) + ' ' + \
                         str(self.real_word_error_channel.mean_errors_per_word) + ' ' + str(self.real_word_error_channel.max_errors_per_word))

        assert results ==  [ \
            u'an 18 man 1.0 19.0 1.0 1', \
                u'an 30 any 2.0 31.0 1.0 1', \
                u'an 92 up 3.0 93.0 1.66666666667 3', \
                u'an 157 ran 4.0 158.0 1.5 3', \
                u'an 215 ran 5.0 216.0 1.4 3', \
                u'an 217 a 6.0 218.0 1.5 3', \
                u'an 219 a 7.0 220.0 1.42857142857 3', \
                u'an 220 and 8.0 221.0 1.375 3', \
                u'an 251 can 9.0 252.0 1.33333333333 3', \
                u'an 252 a 10.0 253.0 1.3 3', \
                u'an 260 in 11.0 261.0 1.27272727273 3', \
                u'an 299 a 12.0 300.0 1.25 3', \
                u'an 327 a 13.0 328.0 1.23076923077 3', \
                u'an 329 a 14.0 330.0 1.21428571429 3', \
                u'an 330 a 15.0 331.0 1.2 3', \
                u'an 365 a 16.0 366.0 1.1875 3', \
                u'an 378 a 17.0 379.0 1.17647058824 3', \
                u'an 391 a 18.0 392.0 1.16666666667 3', \
                u'an 393 a 19.0 394.0 1.15789473684 3', \
                u'an 401 in 20.0 402.0 1.15 3', \
                u'an 409 a 21.0 410.0 1.14285714286 3', \
                u'an 423 a 22.0 424.0 1.13636363636 3', \
                u'an 440 a 23.0 441.0 1.13043478261 3', \
                u'an 448 on 24.0 449.0 1.125 3', \
                u'an 473 and 25.0 474.0 1.12 3', \
                u'an 498 a 26.0 499.0 1.11538461538 3', \
                u'and 42 an 27.0 543.0 1.11111111111 3', \
                u'and 100 an 28.0 601.0 1.10714285714 3', \
                u'and 125 an 29.0 626.0 1.10344827586 3', \
                u'and 126 an 30.0 627.0 1.13333333333 3', \
                u'and 191 an 31.0 692.0 1.12903225806 3', \
                u'and 200 an 32.0 701.0 1.125 3', \
                u'and 244 had 33.0 745.0 1.15151515152 3', \
                u'and 289 an 34.0 790.0 1.14705882353 3', \
                u'and 297 an 35.0 798.0 1.14285714286 3', \
                u'and 302 an 36.0 803.0 1.13888888889 3', \
                u'and 319 an 37.0 820.0 1.13513513514 3', \
                u'and 331 an 38.0 832.0 1.15789473684 3', \
                u'and 362 an 39.0 863.0 1.15384615385 3', \
                u'and 365 an 40.0 866.0 1.15 3', \
                u'and 456 an 41.0 957.0 1.14634146341 3', \
                u'and 463 an 42.0 964.0 1.14285714286 3', \
                u'and 480 a 43.0 981.0 1.16279069767 3', \
                u'the 47 to 44.0 1048.0 1.18181818182 3', \
                u'the 105 t 45.0 1106.0 1.2 3', \
                u'the 123 then 46.0 1124.0 1.19565217391 3', \
                u'the 275 t 47.0 1276.0 1.21276595745 3', \
                u'the 430 get 48.0 1431.0 1.25 3', \
                u'the 497 she 49.0 1498.0 1.24489795918 3', \
                u'there 112 three 50.0 1613.0 1.24 3', \
                u'there 128 three 51.0 1629.0 1.23529411765 3', \
                u'there 133 three 52.0 1634.0 1.23076923077 3', \
                u'there 166 three 53.0 1667.0 1.22641509434 3', \
                u'there 176 three 54.0 1677.0 1.24074074074 3', \
                u'there 223 three 55.0 1724.0 1.23636363636 3', \
                u'there 245 three 56.0 1746.0 1.23214285714 3', \
                u'there 258 three 57.0 1759.0 1.22807017544 3', \
                u'there 272 three 58.0 1773.0 1.22413793103 3', \
                u'there 274 three 59.0 1775.0 1.22033898305 3', \
                u'there 283 where 60.0 1784.0 1.21666666667 3', \
                u'there 305 three 61.0 1806.0 1.2131147541 3', \
                u'there 309 three 62.0 1810.0 1.20967741935 3', \
                u'there 319 three 63.0 1820.0 1.22222222222 3', \
                u'there 325 them 64.0 1826.0 1.234375 3', \
                u'there 343 three 65.0 1844.0 1.23076923077 3', \
                u'there 352 three 66.0 1853.0 1.22727272727 3', \
                u'there 355 the 67.0 1856.0 1.23880597015 3', \
                u'there 495 then 68.0 1996.0 1.25 3', \
                u'late 142 date 69.0 2143.0 1.24637681159 3', \
                u'late 247 lake 70.0 2248.0 1.24285714286 3', \
                u'late 386 later 71.0 2387.0 1.23943661972 3'], results
            



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
