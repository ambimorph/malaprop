# 2012 L. Amber Wilcox-O'Hearn
# RealWordVocabExtractor.py

import codecs, unicodedata

class RealWordVocabExtractor():

    def __init__(self, vocabfile_obj, outfile_obj):
        self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        self.unicode_outfile_obj = codecs.getwriter('utf-8')(outfile_obj)

    def extract_real_words(self):
        """
        My current definition of real word is that it contains
        letters, and if there are symbols in it, they have to be
        either apostrophes or periods.  In addition, it cannot be the
        special end.of.document word in Westbury Lab's Wikipedia.
        """
        for line in self.unicode_vocabfile_obj.readlines():
            word = line.strip()

            if word == u'end.of.document':
                real_word = False

            else:
            
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

    import sys
    rwve = RealWordVocabExtractor(sys.stdin, sys.stdout)
    rwve.extract_real_words()
