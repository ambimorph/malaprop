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
        self.corrupted = StringIO.StringIO()
        p = .3
        r = random.Random(999)
        self.real_word_error_channel = RealWordErrorChannel.RealWordErrorChannel(text_to_corrupt, vocab_file, self.corrupted, p, r)

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
        self.real_word_error_channel.random_number_generator = random.Random(999)
        self.real_word_error_channel.p = .7

        test_cases = [(u'', u'a', u'a'), (u'', u'a', u'n'), (u's', u'a', u'sta'), (u's', u'a', u'as'), (u's', u'', u's'), (u's', u'', u'sz')]

        for t in test_cases:

            try:
                result = self.real_word_error_channel.create_error_with_probability_p(t[0], t[1])
                assert result == t[2]
 
            except AssertionError, exp:
                print  u'Expected ' + t[2] + ', but got ' + result
                self.real_word_error_channel.p = .3
                raise exp

        self.real_word_error_channel.p = .3

    def test_pass_token_through_channel(self):

        self.real_word_error_channel.random_number_generator = random.Random(999)
        self.real_word_error_channel.reset_stats()

        test_tokens = [u'an', u'and', u'the', u'there', u'late', u'"']
        results = []
        for token in test_tokens:
            for i in range(500):
                result = self.real_word_error_channel.pass_token_through_channel(token)
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
        self.real_word_error_channel.random_number_generator = random.Random(999)
        sentences = [ \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 32, 33, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, u'<4-digit-integer>')]), \
            (u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', \
            [5, 6, 14, 15, 24, 25, 30, 31, 36, 37, 40, 41, 44, 45, 47, 48, 51, 52, 58, 59, 60, 66, 67, 78, 79, 81, 82, 85, 86, 89, 90, 92, 93, 98, 99, 104, 105, 106, 109, 110, 114, 115, 117, 118, 126, 127, 134, 135, 144, 145, 146, 154, 155, 160, 161, 163, 164, 168, 169, 174, 175, 179], [])]
        expected_results = [[\
                (13, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School i 1921.'), \
                (19, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.'), \
                (21, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.'), \
                (27, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School i 1921.'), \
                (32, u'Experiments a Germany led to A. S. Neill founding what became Summerhill School in 1921.'), \
                (40, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.'), \
                (41, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School i 1921.'), \
                (46, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School in 1921.'), \
                (48, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.') ], \
               [(0, u'Overt symptoms gradually begin after the age off six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.'), \
                (2, u'Overt symptoms gradually begin after the age of six months, become established by age two on three years, and tend to continue through adulthood, although often in more muted form.'), \
                (3, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted for.'), \
                (4, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, hand tend to continue through adulthood, although often in more muted form.'), \
                (8, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.'), \
                (9, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often win more muted form.'), \
                (11, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend low continue through adulthood, although often in more muted form.'), \
                (13, u'Overt symptoms gradually begin after the age of six months, become established by age two or three year, and tend t continue through adulthood, although often in more muted form.'), \
                (15, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted from.'), \
                (21, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.'), \
                (24, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.'), \
                (28, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.'), \
                (30, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.'), \
                (31, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.'), \
                (32, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted from.'), \
                (33, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.'), \
                (36, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.'), \
                (37, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.'), \
                (40, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.'), \
                (46, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.')]]
                                
        for i in range(len(sentences)):
            sentence_and_token_information = sentences[i]
            expected = expected_results[i]
            results = []
            for i in range(50):
                result = self.real_word_error_channel.pass_sentence_through_channel(sentence_and_token_information)
                if result != sentence_and_token_information[0]:
                    results.append((i, result))

            try:
                assert results == expected
            except AssertionError, exp:
                print sentence_and_token_information[0]
                for res in results: print res
                for i in range(len(results)):
                    if results[i] == expected[i]:
                        print '\nMatched: ', results[i]
                    else:
                        print '\nDid not match: \nGot: ', results[i], '\nExpected: ', expected[i]
                raise exp

    def test_pass_file_through_channel(self):
        self.real_word_error_channel.random_number_generator = random.Random(999)
        self.real_word_error_channel.reset_stats()
        text_to_create_errors_in = u'Autism.\nAutism is a disorder of neural development characterized by impaired social interaction and communication, and by restricted and repetitive behavior. These signs all begin before a child is three years old. Autism affects information processing in the brain by altering how nerve cells and their synapses connect and organize; how this occurs is not well understood. The two other autism spectrum disorders (ASD) are Asperger syndrome, which lacks delays in cognitive development and language, and PDD-NOS, diagnosed when full criteria for the other two disorders are not met.\nAutism has a strong genetic basis, although the genetics of autism are complex and it is unclear whether ASD is explained more by rare mutations, or by rare combinations of common genetic variants. In rare cases, autism is strongly associated with agents that cause birth defects. Controversies surround other proposed environmental causes, such as heavy metals, pesticides or childhood vaccines; the vaccine hypotheses are biologically implausible and lack convincing scientific evidence. The prevalence of autism is about 1–2 per 1,000 people; the prevalence of ASD is about 6 per 1,000, with about four times as many males as females. The number of people diagnosed with autism has increased dramatically since the 1980s, partly due to changes in diagnostic practice; the question of whether actual prevalence has increased is unresolved.\nParents usually notice signs in the first two years of their child\'s life. The signs usually develop gradually, but some autistic children first develop more normally and then regress. Although early behavioral or cognitive intervention can help autistic children gain self-care, social, and communication skills, there is no known cure. Not many children with autism live independently after reaching adulthood, though some become successful. An autistic culture has developed, with some individuals seeking a cure and others believing autism should be tolerated as a difference and not treated as a disorder.'

        expected_text_output = u"Autism.\nAutism is at disorder of neural development characterized by impaired social interaction and communication, and by restricted and repetitive behavior.\nThese signs all begin before a child is three years old.\nAutism affects information processing in the brain by altering how nerve cells and their synapses connect and organize; how this occurs is not well understood.\nThe two other autism spectrum disorders (ASD) are Asperger syndrome, which lacks delays in cognitive development and language, and PDD-NOS, diagnosed when full criteria for the other two disorders are not met.\nAutism has a strong genetic basis, although the genetics of autism are complex and up is unclear whether ASD is explained more by rare mutations, or by rare combinations of common genetic variants.\nIn rare cases, autism is strongly associated with agents that cause birth defects.\nControversies surround other proposed environmental causes, such as heavy metals, pesticides or childhood vaccines; the vaccine hypotheses are biologically implausible and lack convincing scientific evidence.\nThe prevalence of autism is about 1\u20132 per 1,000 people; the prevalence of ASD is about 6 per 1,000, with about four times as many males as females.\nThe number of people diagnosed with autism has increased dramatically since the 1980s, partly due to changes in diagnostic practice; the question of whether actual prevalence has increased is unresolved.\nParents usually notice signs in the first two years of their child's life.\nThe signs usually develop gradually, but some autistic children first develop more normally and then regress.\nAlthough early behavioral or cognitive intervention can help autistic children gain self-care, social, and communication skills, there is no known cure.\nNot many children with autism live independently after reaching adulthood, though some become successful.\nAn autistic culture has developed, with some individuals seeking a cure and others believing autism should be tolerated as i difference and not treated as a disorder.\n"

        expected_error_rate = 0.0180722891566
        expected_mean_errors_per_word = 1.66666666667
        expected_max_errors_per_word = 3

        error_rate, mean_errors_per_word, max_errors_per_word = self.real_word_error_channel.pass_file_through_channel(text=text_to_create_errors_in)
        
        print error_rate, mean_errors_per_word, max_errors_per_word
        print self.real_word_error_channel.real_word_tokens_passed_though

        assert isinstance(self.corrupted.getvalue(), unicode), (type(self.corrupted.getvalue()), repr(self.corrupted.getvalue()))
        try:
            assert self.corrupted.getvalue() == expected_text_output
        except AssertionError, exp:
            x = self.corrupted.getvalue()
            for i in range(len(x)):
                if i >= len(expected_text_output) or x[i] != expected_text_output[i]: break
            print '\nMatching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_text_output[i:])
            raise exp

        tolerance = 0.000001
        assert abs(error_rate - expected_error_rate) < tolerance, "Expected error_rate " + str(expected_error_rate) + ", but got " + str(error_rate)
        assert abs(mean_errors_per_word - expected_mean_errors_per_word) < tolerance, "Expected mean_errors_per_word " + str(expected_mean_errors_per_word) + ", but got " + str(mean_errors_per_word)
        assert abs(max_errors_per_word - expected_max_errors_per_word) < tolerance, "Expected max_errors_per_word-rate " + str(expected_max_errors_per_word) + ", but got " + str(max_errors_per_word)
        
if __name__ == '__main__':
    unittest.main()
