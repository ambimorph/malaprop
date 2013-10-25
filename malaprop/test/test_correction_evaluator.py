# test_correction_evaluator.py

from malaprop.evaluation import correction_evaluator
import unittest, StringIO

xxy = 'False Positive'
xyx = 'True Positive'
xyy = 'False Negative'
xyz = 'Detection True Positive, Correction False Negative, Correction False Positive'

class CorrectionEvaluatorTest(unittest.TestCase):
    
    def test_classify_instances_assertions_met(self):

        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = None, a, b, c
        with self.assertRaises(AssertionError):
            correction_evaluator.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, b, None, c
        with self.assertRaises(AssertionError):
            correction_evaluator.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, a, None, None
        with self.assertRaises(AssertionError):
            correction_evaluator.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = None, None, a, a
        with self.assertRaises(AssertionError):
            correction_evaluator.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, b, c, a
        with self.assertRaises(AssertionError):
            correction_evaluator.classify_correction_instance(original, error, observed, correction)

    def test_classify_instances_xxy(self):

        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = None, None, a, b
        result = correction_evaluator.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(result, xxy), result

    def test_classify_instances_xyx(self):

        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, b, a
        result = correction_evaluator.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(result, xyx), result

    def test_classify_instances_xyy(self):

        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, None, None
        result = correction_evaluator.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(result, xyy), result

    def test_classify_instances_xyz(self):

        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, b, c
        result = correction_evaluator.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(result, xyz), result




        
if __name__ == '__main__':
    unittest.main()
