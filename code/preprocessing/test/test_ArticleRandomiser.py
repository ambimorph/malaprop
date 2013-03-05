# L. Amber Wilcox-O'Hearn 2011
# test_ArticleRandomiser.py

from code.preprocessing import ArticleRandomiser
import unittest, StringIO, random


class ArticleRandomiserTest(unittest.TestCase):

    def test_randomise(self):

        r = random.Random(999)

        a1 = ["Anarchism.\n", "Anarchism is a political philosophy which considers the state undesirable, unnecessary and harmful, and instead promotes a stateless society, or anarchy. It seeks to diminish or even abolish authority in the conduct of human relations. Anarchists may widely disagree on what additional criteria are required in anarchism. \"The Oxford Companion to Philosophy\" says, \"there is no single defining position that all anarchists hold, and those considered anarchists at best share a certain family resemblance.\"", "---END.OF.DOCUMENT---\n"]
        a2 = ["Hidehiko Shimizu.\n", "Hidehiko Shimizu (born 4 November 1954) is a former Japanese football player. He has played for Nissan Motors.\n", "---END.OF.DOCUMENT---\n"]
        a3 = ["Some other thing.\n", "this\n", "could\n", "be a line or three.\n", "---END.OF.DOCUMENT---\n"]
        a4 = ["Finally.\n", "Another one.\n", "---END.OF.DOCUMENT---\n"]

        newline_list = ["\n"]

        article_file_obj = a1 + newline_list + a2 + newline_list + a3 + newline_list + a4

        train_file_obj = StringIO.StringIO()
        devel_file_obj = StringIO.StringIO()
        test_file_obj = StringIO.StringIO()

        ar = ArticleRandomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, r)
        ar.randomise()
        assert train_file_obj.getvalue() == "".join(a2+a4), "".join(a2+a4) + train_file_obj.getvalue()
        assert devel_file_obj.getvalue() == "".join(a1), "".join(a1) + devel_file_obj.getvalue()
        assert test_file_obj.getvalue() == "".join(a3),  "".join(a3) + test_file_obj.getvalue() 

if __name__ == '__main__':
    unittest.main()
