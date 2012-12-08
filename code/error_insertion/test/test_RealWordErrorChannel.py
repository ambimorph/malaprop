# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_RealWordErrorChannel.py

from code.preprocessing import NLTKSegmentThenTokenise
from code.error_insertion import RealWordErrorChannel
import unittest, random, StringIO


class RealWordErrorChannelTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        text_to_corrupt = open('test_data/segmenter_training', 'rb')
        vocab_file = open('test_data/1K_test_real_word_vocab', 'rb')
        self.corrupted_file = StringIO.StringIO()
        self.corrections_file = StringIO.StringIO()
        p = .3
        r = random.Random(999)
        self.real_word_error_channel = RealWordErrorChannel.RealWordErrorChannel(text_to_corrupt, vocab_file, self.corrupted_file, self.corrections_file, p, r)

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
                         str(self.real_word_error_channel.real_word_tokens_passed_through) + ' ' + \
                         str(self.real_word_error_channel.mean_errors_per_word) + ' ' + str(self.real_word_error_channel.max_errors_per_word))

        try:

            assert results == \
                [u'an 23 a 1.0 24.0 1.0 1', u'an 32 any 2.0 33.0 1.0 1', u'an 65 on 3.0 66.0 1.0 1', u'an 94 up 4.0 95.0 1.5 3', u'an 132 met 5.0 133.0 2.0 4', u'an 136 t 6.0 137.0 2.0 4', u'an 160 a 7.0 161.0 1.85714285714 4', u'an 162 on 8.0 163.0 1.75 4', u'an 220 ran 9.0 221.0 1.66666666667 4', u'an 224 a 10.0 225.0 1.6 4', u'an 225 and 11.0 226.0 1.54545454545 4', u'an 229 san 12.0 230.0 1.5 4', u'an 259 can 13.0 260.0 1.46153846154 4', u'an 260 a 14.0 261.0 1.42857142857 4', u'an 310 a 15.0 311.0 1.4 4', u'an 339 a 16.0 340.0 1.375 4', u'an 341 a 17.0 342.0 1.35294117647 4', u'an 342 a 18.0 343.0 1.33333333333 4', u'an 350 a 19.0 351.0 1.31578947368 4', u'an 351 a 20.0 352.0 1.3 4', u'an 352 no 21.0 353.0 1.33333333333 4', u'an 380 a 22.0 381.0 1.31818181818 4', u'an 393 a 23.0 394.0 1.30434782609 4', u'an 407 a 24.0 408.0 1.29166666667 4', u'an 409 a 25.0 410.0 1.28 4', u'an 425 a 26.0 426.0 1.26923076923 4', u'an 430 i 27.0 431.0 1.2962962963 4', u'an 435 al 28.0 436.0 1.32142857143 4', u'an 439 a 29.0 440.0 1.31034482759 4', u'an 458 a 30.0 459.0 1.3 4', u'an 466 on 31.0 467.0 1.29032258065 4', u'an 492 and 32.0 493.0 1.28125 4', u'and 5 an 33.0 506.0 1.27272727273 4', u'and 57 an 34.0 558.0 1.26470588235 4', u'and 87 an 35.0 588.0 1.25714285714 4', u'and 116 an 36.0 617.0 1.25 4', u'and 141 an 37.0 642.0 1.24324324324 4', u'and 217 an 38.0 718.0 1.23684210526 4', u'and 309 an 39.0 810.0 1.23076923077 4', u'and 318 an 40.0 819.0 1.225 4', u'and 323 an 41.0 824.0 1.21951219512 4', u'and 341 an 42.0 842.0 1.21428571429 4', u'and 385 an 43.0 886.0 1.20930232558 4', u'and 428 end 44.0 929.0 1.20454545455 4', u'and 483 an 45.0 984.0 1.2 4', u'and 487 an 46.0 988.0 1.19565217391 4', u'the 8 t 47.0 1009.0 1.21276595745 4', u'the 12 he 48.0 1013.0 1.20833333333 4', u'the 20 then 49.0 1021.0 1.20408163265 4', u'the 25 they 50.0 1026.0 1.2 4', u'the 83 he 51.0 1084.0 1.19607843137 4', u'the 141 he 52.0 1142.0 1.23076923077 4', u'the 155 then 53.0 1156.0 1.22641509434 4', u'the 213 re 54.0 1214.0 1.24074074074 4', u'the 214 de 55.0 1215.0 1.25454545455 4', u'the 310 t 56.0 1311.0 1.26785714286 4', u'the 354 he 57.0 1355.0 1.26315789474 4', u'the 355 yet 58.0 1356.0 1.29310344828 4', u'the 364 he 59.0 1365.0 1.28813559322 4', u'the 457 he 60.0 1458.0 1.28333333333 4', u'the 458 them 61.0 1459.0 1.27868852459 4', u'the 467 get 62.0 1468.0 1.3064516129 4', u'the 479 he 63.0 1480.0 1.30158730159 4', u'the 490 he 64.0 1491.0 1.296875 4', u'the 496 he 65.0 1497.0 1.29230769231 4', u'there 3 three 66.0 1504.0 1.28787878788 4', u'there 9 here 67.0 1510.0 1.28358208955 4', u'there 56 three 68.0 1557.0 1.27941176471 4', u'there 82 here 69.0 1583.0 1.27536231884 4', u'there 134 here 70.0 1635.0 1.27142857143 4', u'there 140 three 71.0 1641.0 1.2676056338 4', u'there 156 three 72.0 1657.0 1.26388888889 4', u'there 161 three 73.0 1662.0 1.2602739726 4', u'there 204 re 74.0 1705.0 1.28378378378 4', u'there 208 three 75.0 1709.0 1.28 4', u'there 254 three 76.0 1755.0 1.27631578947 4', u'there 255 here 77.0 1756.0 1.27272727273 4', u'there 266 here 78.0 1767.0 1.26923076923 4', u'there 290 three 79.0 1791.0 1.26582278481 4', u'there 304 three 80.0 1805.0 1.2625 4', u'there 306 three 81.0 1807.0 1.25925925926 4', u'there 334 the 82.0 1835.0 1.26829268293 4', u'there 338 three 83.0 1839.0 1.26506024096 4', u'there 342 three 84.0 1843.0 1.2619047619 4', u'there 377 three 85.0 1878.0 1.25882352941 4', u'there 386 here 86.0 1887.0 1.25581395349 4', u'there 390 the 87.0 1891.0 1.26436781609 4', u'there 443 here 88.0 1944.0 1.26136363636 4', u'late 189 date 89.0 2190.0 1.25842696629 4', u'late 241 la 90.0 2242.0 1.26666666667 4', u'late 436 later 91.0 2437.0 1.26373626374 4'], results

        except AssertionError, exp:
            for line in results: print line
            raise exp

    def test_pass_sentence_through_channel(self):
        self.real_word_error_channel.random_number_generator = random.Random(79)
        sentences = [ \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 32, 33, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, u'<4-digit-integer>')]), \
            (u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', \
            [5, 6, 14, 15, 24, 25, 30, 31, 36, 37, 40, 41, 44, 45, 47, 48, 51, 52, 58, 59, 60, 66, 67, 78, 79, 81, 82, 85, 86, 89, 90, 92, 93, 98, 99, 104, 105, 106, 109, 110, 114, 115, 117, 118, 126, 127, 134, 135, 144, 145, 146, 154, 155, 160, 161, 163, 164, 168, 169, 174, 175, 179], [])]
        expected_results = [[\
                (4, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]), \
                (8, u'Experiments in Germany led it A. S. Neill founding what became Summerhill School in 1921.', [(27, u'it', u'to')]), \
                (10, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]), \
                (14, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School i 1921.', [(81, u'i', u'in')]), \
                (20, u'Experiments in Germany led t A. S. Neill founding what became Summerhill School in 1921.', [(27, u't', u'to')]), \
                (23, u'Experiments in Germany led to A. S. Neill founding what came Summerhill School in 1921.', [(56, u'came', u'became')]), \
                (27, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]), \
                (28, u'Experiments i Germany led t A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in'), (27, u't', u'to')]), \
                (29, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]), \
                (32, u'Experiments in Germany led to A. S. Neill founding at became Summerhill School in 1921.', [(51, u'at', u'what')]), \
                (35, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School an 1921.', [(81, u'an', u'in')]), \
                (44, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School ii 1921.', [(81, u'ii', u'in')]), \
                (45, u'Experiments it Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'it', u'in')]), \
                (62, u'Experiments in Germany led to A. S. Neill founding what became Summerhill School i 1921.', [(81, u'i', u'in')]), \
                (79, u'Experiments i Germany led to A. S. Neill founding what became Summerhill School in 1921.', [(12, u'i', u'in')]), \
                     ], \
               [ (1, u'Overt symptoms gradually begin after the age of six months, become established by as two or three years, and tend to continue through adulthood, although often in more muted form.', [(82, u'as', u'age')]), \
                 (4, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.', [(106, u'an', u'and')]), \
                 (10, u'Overt symptoms gradually begin after the age of six months, become established by a two or three years, and tend to continue through adulthood, though often in more muted form.', [(82, u'a', u'age'), (146, u'though', u'although')]), \
                 (14, u'Overt symptoms gradually begin after he age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted form.', [(37, u'he', u'the')]), \
                 (16, u'Overt symptoms gradually begin after the age of six months, become established by age two a here years, and tend to continue through adulthood, although often in more muted form.', [(90, u'a', u'or'), (93, u'here', u'three')]), \
                 (19, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in or muted form.', [(164, u'or', u'more')]), \
                 (22, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.', [(115, u't', u'to')]), \
                 (29, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.', [(115, u't', u'to')]), \
                 (33, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, and tend to continue through adulthood, although often in more muted form.', [(79, u'b', u'by')]), \
                 (40, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.', [(106, u'an', u'and')]), \
                 (46, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often an more muted form.', [(161, u'an', u'in')]), \
                 (49, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often i more muted form.', [(161, u'i', u'in')]), \
                 (52, u'Overt symptoms gradually begin after the age of six months, become established b age two or three years, said tend to continue through adulthood, although often win more muted form.', [(79, u'b', u'by'), (106, u'said', u'and'), (161, u'win', u'in')]), \
                 (54, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.', [(86, u'to', u'two')]), \
                 (62, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in more muted from.', [(175, u'from', u'form')]), \
                 (64, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.', [(115, u't', u'to')]), \
                 (68, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend to continue through adulthood, although often in re muted form.', [(164, u're', u'more')]), \
                 (69, u'Overt symptoms gradually begin after the age of six months, become established by age to or three years, and tend to continue through adulthood, although often in more muted form.', [(86, u'to', u'two')]), \
                 (71, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, and tend t continue through adulthood, although often in more muted form.', [(115, u't', u'to')]), \
                 (77, u'Overt symptoms gradually begin after the age of six months, become established by age two or three year, and tend to continue through adulthood, although often in more muted form.', [(99, u'year', u'years')]), \
                 (78, u'Overt symptoms gradually begin after the age of six months, become established by age two or three years, an tend to continue through adulthood, although often in more muted form.', [(106, u'an', u'and')]), \
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

    def test_pass_file_through_channel(self):
        self.real_word_error_channel.random_number_generator = random.Random(999)
        self.real_word_error_channel.reset_stats()
        text_to_create_errors_in = u'Autism.\nAutism is a disorder of neural development characterized by impaired social interaction and communication, and by restricted and repetitive behavior. These signs all begin before a child is three years old. Autism affects information processing in the brain by altering how nerve cells and their synapses connect and organize; how this occurs is not well understood. The two other autism spectrum disorders (ASD) are Asperger syndrome, which lacks delays in cognitive development and language, and PDD-NOS, diagnosed when full criteria for the other two disorders are not met.\nAutism has a strong genetic basis, although the genetics of autism are complex and it is unclear whether ASD is explained more by rare mutations, or by rare combinations of common genetic variants. In rare cases, autism is strongly associated with agents that cause birth defects. Controversies surround other proposed environmental causes, such as heavy metals, pesticides or childhood vaccines; the vaccine hypotheses are biologically implausible and lack convincing scientific evidence. The prevalence of autism is about 1–2 per 1,000 people; the prevalence of ASD is about 6 per 1,000, with about four times as many males as females. The number of people diagnosed with autism has increased dramatically since the 1980s, partly due to changes in diagnostic practice; the question of whether actual prevalence has increased is unresolved.\nParents usually notice signs in the first two years of their child\'s life. The signs usually develop gradually, but some autistic children first develop more normally and then regress. Although early behavioral or cognitive intervention can help autistic children gain self-care, social, and communication skills, there is no known cure. Not many children with autism live independently after reaching adulthood, though some become successful. An autistic culture has developed, with some individuals seeking a cure and others believing autism should be tolerated as a difference and not treated as a disorder.'

        expected_text_output = "Autism.\nAutism is at disorder of neural development characterized by impaired social interaction and communication, and b restricted and repetitive behavior.\nThese signs all begin before a child is three years old.\nAutism affects information processing in the brain by altering how nerve cells and their synapses connect and organize; how this occurs is not well understood.\nThe two other autism spectrum disorders (ASD) are Asperger syndrome, which lacks delays in cognitive development and language, and PDD-NOS, diagnosed when full criteria for the other two disorders are not met.\nAutism has a strong genetic basis, although the genetics of autism are complex and it is unclear whether ASD is explained more by rare mutations, or by rare combinations of common genetic variants.\nIn rare cases, autism is strongly associated with agents that cause birth defects.\nControversies surround other proposed environmental causes, such as heavy metals, pesticides or childhood vaccines; be vaccine hypotheses are biologically implausible and lack convincing scientific evidence.\nThe prevalence of autism is about 1\xe2\x80\x932 per 1,000 people; the prevalence of ASD is about 6 per 1,000, with about four times as many males as females.\nThe number of people diagnosed with autism has increased dramatically since the 1980s, partly due to changes in diagnostic practice; the question of whether actual prevalence has increased is unresolved.\nParents usually notice signs in the first two years of their child's life.\nThe signs usually develop gradually, but some autistic children first develop more normally and he regress.\nAlthough early behavioral or cognitive intervention can help autistic children gain self-care, social, and communication skills, there is no known cure.\nNot many children with autism live independently after reaching adulthood, though some become successful.\nAn autistic culture has developed, with some individuals seeking a cure and others believing autism should be tolerated days a difference and not treated as a disorder.\n"

        expected_corrections_output = "1 [(10, u'at', u'a'), (111, u'b', u'by')]\n7 [(116, u'be', u'the')]\n11 [(96, u'he', u'then')]\n14 [(120, u'days', u'as')]\n(5.0, 166.0, 1.6, 2)"

        self.real_word_error_channel.pass_file_through_channel(text=text_to_create_errors_in)
        
        for got, expected in [(self.corrupted_file.getvalue(), expected_text_output), (self.corrections_file.getvalue(), expected_corrections_output)]:
            assert isinstance(got, str), (type(got), repr(got))
            try:
                assert got == expected
            except AssertionError, exp:
                x = got
                for i in range(len(x)):
                    if i >= len(expected) or x[i] != expected[i]: break
                print '\nMatching prefix of output and expected output: ', repr(x[:i])
                print '\noutput differs starting here: ', repr(x[i:])
                print '\nexpected: ', repr(expected[i:])
                raise exp

        expected_real_word_errors = 5
        expected_real_word_tokens_passed_through = 166
        expected_mean_errors_per_word = 1.6
        expected_max_errors_per_word = 2

        real_word_errors, real_word_tokens_passed_through, mean_errors_per_word, max_errors_per_word \
            = self.real_word_error_channel.get_stats()

        tolerance = 0.000001
        assert abs(expected_real_word_errors - real_word_errors) < tolerance, \
            "Expected real word errors " + str(expected_real_word_errors) + ", but got " + str(real_word_errors)
        assert abs(expected_real_word_tokens_passed_through - real_word_tokens_passed_through) < tolerance, \
            "Expected real_word_tokens_passed_through " + str(expected_real_word_tokens_passed_through) + ", but got " + str(real_word_tokens_passed_through)
        assert abs(mean_errors_per_word - expected_mean_errors_per_word) < tolerance, \
            "Expected mean_errors_per_word " + str(expected_mean_errors_per_word) + ", but got " + str(mean_errors_per_word)
        assert abs(max_errors_per_word - expected_max_errors_per_word) < tolerance, "\
            Expected max_errors_per_word-rate " + str(expected_max_errors_per_word) + ", but got " + str(max_errors_per_word)
        
if __name__ == '__main__':
    unittest.main()
