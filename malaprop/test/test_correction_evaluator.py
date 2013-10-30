# test_correction_evaluator.py

from malaprop.evaluation.correction_evaluator import *
import unittest, StringIO

xxy = 'False Positive'
xyx = 'True Positive'
xyy = 'False Negative'
xyz = 'Detection True Positive, Correction False Negative, Correction False Positive'

class CorrectionEvaluatorTest(unittest.TestCase):
    
    def test_classify_instances_assertions_met(self):

        ce = CorrectionEvaluator()
        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = None, a, b, c
        with self.assertRaises(AssertionError):
            ce.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, b, None, c
        with self.assertRaises(AssertionError):
            ce.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, a, None, None
        with self.assertRaises(AssertionError):
            ce.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = None, None, a, a
        with self.assertRaises(AssertionError):
            ce.classify_correction_instance(original, error, observed, correction)

        original, error, observed, correction = a, b, c, a
        with self.assertRaises(AssertionError):
            ce.classify_correction_instance(original, error, observed, correction)

    def test_classify_instances_xxy(self):

        ce = CorrectionEvaluator()
        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = None, None, a, b
        ce.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(ce.detection_true_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_true_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.detection_false_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.correction_false_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.detection_false_negatives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_negatives, 0), ce.detection_true_positives
        self.assertDictEqual(ce.distributions[xxy], {(a,b):1}), ce.distributions
        self.assertDictEqual(ce.distributions[xyx], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyz], {}), ce.distributions

    def test_classify_instances_xyx(self):

        ce = CorrectionEvaluator()
        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, b, a
        ce.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(ce.detection_true_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.correction_true_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.detection_false_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.detection_false_negatives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_negatives, 0), ce.detection_true_positives
        self.assertDictEqual(ce.distributions[xxy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyx], {(b,a):1}), ce.distributions
        self.assertDictEqual(ce.distributions[xyy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyz], {}), ce.distributions

    def test_classify_instances_xyy(self):

        ce = CorrectionEvaluator()
        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, None, None
        ce.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(ce.detection_true_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_true_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.detection_false_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.detection_false_negatives, 1), ce.detection_true_positives
        self.assertEqual(ce.correction_false_negatives, 1), ce.detection_true_positives
        self.assertDictEqual(ce.distributions[xxy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyx], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyy], {(b,a):1}), ce.distributions
        self.assertDictEqual(ce.distributions[xyz], {}), ce.distributions

    def test_classify_instances_xyz(self):

        ce = CorrectionEvaluator()
        a, b, c = 'a', 'b', 'c'

        original, error, observed, correction = a, b, b, c
        ce.classify_correction_instance(original, error, observed, correction)
        self.assertEqual(ce.detection_true_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.correction_true_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.detection_false_positives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.detection_false_negatives, 0), ce.detection_true_positives
        self.assertEqual(ce.correction_false_negatives, 1), ce.detection_true_positives
        self.assertDictEqual(ce.distributions[xxy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyx], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyy], {}), ce.distributions
        self.assertDictEqual(ce.distributions[xyz], {(b,a,c):1}), ce.distributions

    def test_process_all_corrections(self):

        ce = CorrectionEvaluator()
        true_corrections_file = StringIO.StringIO(u'[4, [[10, 0, "boy", "body"]]]\n[6, [[9, 0, "so", "to"]]]\n[12, [[2, 0, "causes", "cases"], [11, 0, "top", "to"], [22, 0, "re", "are"]]]\n')
        proposed_corrections_file = StringIO.StringIO(u'[3, [[6, 0, "off", "of"]]]\n[4, [[10, 0, "boy", "body"]]]\n[12, [[2, 0, "causes", "cases"], [11, 0, "top", "stop"]]]\n')
        ce.process_all_corrections(true_corrections_file, proposed_corrections_file)
        self.assertEqual(ce.detection_true_positives, 3), ce.detection_true_positives
        self.assertEqual(ce.correction_true_positives, 2), ce.detection_true_positives
        self.assertEqual(ce.detection_false_positives, 1), ce.detection_true_positives
        self.assertEqual(ce.correction_false_positives, 2), ce.detection_true_positives
        self.assertEqual(ce.detection_false_negatives, 2), ce.detection_true_positives
        self.assertEqual(ce.correction_false_negatives, 3), ce.detection_true_positives
        self.assertDictEqual(ce.distributions[xxy], Counter({(u'off', u'of'): 1})), ce.distributions
        self.assertDictEqual(ce.distributions[xyx], Counter({(u'boy', u'body'): 1, (u'causes', u'cases'): 1})), ce.distributions
        self.assertDictEqual(ce.distributions[xyy], Counter({(u're', u'are'): 1, (u'so', u'to'): 1})), ce.distributions
        self.assertDictEqual(ce.distributions[xyz], Counter({(u'top', u'to', u'stop'): 1})), ce.distributions


    
if __name__ == '__main__':
    unittest.main()
