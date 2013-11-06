# test_adversarial_evaluator.py

from malaprop.evaluation.adversarial_evaluator import *
import unittest, StringIO


class AdversarialEvaluatorTest(unittest.TestCase):

    def test_report_accuracy(self):

        key_file = StringIO.StringIO('00100010111')
        proposed_file = StringIO.StringIO('01010101010')

        result = report_accuracy(key_file, proposed_file)
        expected_result = 0.27272727
        self.assertAlmostEqual(result, expected_result), result

    def test_report_accuracy_and_errors(self):

        key_file = StringIO.StringIO('00000000')
        proposed_file = StringIO.StringIO('01010101')
        adversarial_file = StringIO.StringIO('a\nb\nc\nd\ne\nf\ng\nh\n')

        acc, errs = report_accuracy_and_errors(key_file, proposed_file, adversarial_file)
        expected_accuracy = 0.5
        expected_errs =  ['b\n', 'd\n', 'f\n', 'h\n', ]
        self.assertAlmostEqual(acc, expected_accuracy), acc
        self.assertListEqual(errs, expected_errs), errs


if __name__ == '__main__':
    unittest.main()

