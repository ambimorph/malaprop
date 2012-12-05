# 2012 L. Amber Wilcox-O'Hearn
# RealWordVocabExtractor.py

import codecs, unicodedata

class RealWordVocabExtractor():

    def __init__(self, vocabfile_obj, outfile_obj):
        self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        self.unicode_outfile_obj = codecs.getwriter('utf-8')(outfile_obj)

    def extract_real_words(self):
        for line in self.unicode_vocabfile_obj.readlines():
            word = line.strip()
            
            contains_letters = False
            real_word = True
            for char in word:
                if unicodedata.category(char)[0] == 'L':
                    contains_letters = True
                elif char != u'.' and char != u"'":
                    real_word = False
                    break
            if not contains_letters: real_word = False

            if real_word:
                self.unicode_outfile_obj.write(word + u'\n')


if __name__ == '__main__':

    rwve = RealWordVocabExtractor(sys.stdin, sys.stdout)
    rwve.extract_real_words()
