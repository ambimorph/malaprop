# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_RealWordVocabExtractor.py

from code.error_insertion import RealWordVocabExtractor
import unittest, StringIO


class RealWordVocabExtractorTest(unittest.TestCase):
    
    def test_real_word_vocab_extactor(self):
        vocab_file_obj = open('code/error_insertion/test/test_data/1K_test_vocab', 'rb')
        outfile_obj = StringIO.StringIO()
        real_word_vocab_extractor = RealWordVocabExtractor.RealWordVocabExtractor(vocab_file_obj, outfile_obj)
        real_word_vocab_extractor.extract_real_words()
        vocabulary = outfile_obj.getvalue()
        for test_word in [u'with', u'end', u'don\'t']:
            assert vocabulary.find(u'\n' + test_word + u'\n') != -1, test_word
        for test_word in [u'xxxx', u'-', u'.', u'<3-digit-integer>', u'end.of.document']:
            assert vocabulary.find(u'\n' + test_word + u'\n') == -1, test_word

        
if __name__ == '__main__':
    unittest.main()
