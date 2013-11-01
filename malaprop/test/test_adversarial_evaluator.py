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
