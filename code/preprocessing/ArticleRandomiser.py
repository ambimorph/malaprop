# L. Amber Wilcox-O'Hearn 2011
# ArticleRandomiser.py

# The Westbury Lab Corpus consists of a single file containing all and only the
# text of the articles of Wikipedia.  Each article begins with a title on a
# single line, and ends with "---END.OF.DOCUMENT---\n\n"
#
# This script will create three directories: train, devel, and test, containing
# approximately 60%, 20%, and 20% respectively of the total text, in a random
# order.  

import sys, random

class Randomiser():
    def __init__(self, article_file_obj, train_file_obj, devel_file_obj, test_file_obj, rand_obj):
        self.article_file_obj = article_file_obj
        self.train_file_obj = train_file_obj
        self.devel_file_obj = devel_file_obj
        self.test_file_obj = test_file_obj
        self.rand_obj = rand_obj

    def choose_outfile(self):
        x = self.rand_obj.random()
        if x < .6: return self.train_file_obj
        if x < .8: return self.devel_file_obj
        return self.test_file_obj
        
    def randomise(self):
        blank_between_articles = False
        outfile = self.choose_outfile()
        for line in self.article_file_obj:
            if line == "---END.OF.DOCUMENT---\n":
                outfile.write(line)
                blank_between_articles = True
            elif blank_between_articles:
                outfile = self.choose_outfile()
                blank_between_articles = False
            else:
                outfile.write(line)


if __name__ == '__main__':
    article_file_obj = sys.stdin
    train_file_obj = open("train", 'w')
    devel_file_obj = open("devel", 'w')
    test_file_obj = open("test", 'w')
    r = random.Random(7)
    ar = Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, r)
    ar.randomise()
