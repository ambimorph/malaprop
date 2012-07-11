# Copyright 2011 L. Amber Wilcox-O'Hearn
# test_vocabulary_cutter.py

import vocabulary_cutter, unittest, StringIO


class VocabularyCutterTest(unittest.TestCase):

    def test_cut_vocabulary(self):

        infile_obj = open('test/data/unigram_counts', 'r')
        outfile_obj = StringIO.StringIO()

        vc = vocabulary_cutter.VocabularyCutter(infile_obj, outfile_obj)
        vc.cut_vocabulary(5)

        assert outfile_obj.getvalue() == "being\nheld\nGer\ndeficits\nChris\n", outfile_obj.getvalue()

if __name__ == '__main__':
    unittest.main()
