# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_real_word_vocab_extractor.py

from malaprop.error_insertion import real_word_vocabulary_extractor
import unittest, StringIO


class RealWordVocabExtractorTest(unittest.TestCase):
    
    def test_real_word_vocab_extactor(self):
        vocab_file_obj = open('malaprop/test/data/1K_test_vocab', 'rb')
        outfile_obj = StringIO.StringIO()
        rwve = real_word_vocabulary_extractor.RealWordVocabExtractor(vocab_file_obj, outfile_obj)
        rwve.extract_real_words()
        vocabulary = outfile_obj.getvalue()
        for test_word in [u'with', u'end', u'don\'t']:
            assert vocabulary.find(u'\n' + test_word + u'\n') != -1, test_word
        for test_word in [u'xxxx', u'-', u'.', u'<3-digit-integer>', u'end.of.document']:
            assert vocabulary.find(u'\n' + test_word + u'\n') == -1, test_word

    def test_no_unicode(self):
        vocab_file_obj = StringIO.StringIO('Some\nascii\nwords\nand\nthen\n\xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82\n')
        outfile_obj = StringIO.StringIO()
        rwve = real_word_vocabulary_extractor.RealWordVocabExtractor(vocab_file_obj, outfile_obj)
        rwve.extract_real_words()
        vocabulary = outfile_obj.getvalue()
        for test_word in [u'ascii', u'and', u'words']:
            assert vocabulary.find(u'\n' + test_word + u'\n') != -1, test_word
        for test_word in [u'\xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82']:
            assert vocabulary.find(u'\n' + test_word + u'\n') == -1, test_word
        

        
if __name__ == '__main__':
    unittest.main()
