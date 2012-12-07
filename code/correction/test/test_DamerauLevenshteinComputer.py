# -*- coding: utf-8 -*-
# 2012 L. Amber Wilcox-O'Hearn
# test_DamerauLevenshteinComputer.py

from code.correction import DamerauLevenshteinComputer
import unittest, StringIO


class DamerauLevenshteinComputerTest(unittest.TestCase):
    
    def test_dameraulevenshtein(self):
        dlc = DamerauLevenshteinComputer.DamerauLevenshteinComputer()
        distances = []
        for pair in [('ba', 'abc'), ('fee', 'deed'), ('', 'do'), ('there', 'three'), ('up', 'in')]:
            distances.append(dlc.dameraulevenshtein(*pair))
        expected_distances = [2, 2, 2, 1, 2]
        assert distances == expected_distances, repr(distances) + repr(expected_distances)

    def test_compute_all_distances_from_vocab(self):
        vocab_file_obj = StringIO.StringIO()
        vocab_file_obj.write("this\nis\na\ntest\n")
        vocab_file_obj.seek(0)
        outfile_obj = StringIO.StringIO()
        expected_output = 'is this 2\na this 4\na is 2\ntest this 3\nis test 3\na test 4\n'
        dlc = DamerauLevenshteinComputer.DamerauLevenshteinComputer(vocab_file_obj, outfile_obj)
        dlc.compute_all_distances_from_vocab()

        assert isinstance(outfile_obj.getvalue(), str), (type(outfile_obj.getvalue()), repr(outfile_obj.getvalue()))
        try:
            assert outfile_obj.getvalue() == expected_output
        except AssertionError, exp:
            x = outfile_obj.getvalue()
            for i in range(len(x)):
                if i >= len(expected_output) or x[i] != expected_output[i]: break
            print '\nMatching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_output[i:])
            raise exp
        

        
if __name__ == '__main__':
    unittest.main()
