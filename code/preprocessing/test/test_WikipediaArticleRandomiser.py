# Copyright 2011 L. Amber Wilcox-O'Hearn
# test_WikipediaArticleRandomiser.py

from code.preprocessing import WikipediaArticleRandomiser
import unittest, StringIO, random


class WikipediaArticleRandomiserTest(unittest.TestCase):

    def test_randomise(self):

        r = random.Random(999)

        a1 = ["John gammon.\n", "Birth Through Elementary School.\n", 'John Michael Gammon was born on April 7, 1991 to Melinda Jane Gammon and William P. Oakes. Unfortunately William "Big Willy" was killed before the birth of the soon to come "Prince of America".\n', "John knew how to speak before he could even suck the milk from his mothers tit. He could read before he could walk. He could do Geometry before he could do basic multiplication. When he was in kindergarden he knew more than his teacher, thus earning him a place among the fifth graders at only five years old. Until the government took him hostage and wiped his memory and destroying all he had accomplished.\n", "---END.OF.DOCUMENT---\n"]
        a2 = ["Hidehiko Shimizu.\n", "Hidehiko Shimizu (born 4 November 1954) is a former Japanese football player. He has played for Nissan Motors.\n", "---END.OF.DOCUMENT---\n"]
        a3 = ["Some other thing.\n", "this\n", "could\n", "be a line or three.\n", "---END.OF.DOCUMENT---\n"]
        a4 = ["Finally.\n", "Another one.\n", "---END.OF.DOCUMENT---\n"]

        newline_list = ["\n"]

        article_file_obj = a1 + newline_list + a2 + newline_list + a3 + newline_list + a4

        train_file_obj = StringIO.StringIO()
        devel_file_obj = StringIO.StringIO()
        test_file_obj = StringIO.StringIO()

        ar = WikipediaArticleRandomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, r)
        ar.randomise()
        assert train_file_obj.getvalue() == "".join(a2+a4), "".join(a2+a4) + train_file_obj.getvalue()
        assert devel_file_obj.getvalue() == "".join(a1), "".join(a1) + devel_file_obj.getvalue()
        assert test_file_obj.getvalue() == "".join(a3),  "".join(a3) + test_file_obj.getvalue() 

if __name__ == '__main__':
    unittest.main()
