# correction_evaluator.py

"""
Precision and recall
--------------------

Normally, to calculate precision and recall, we count true positives, false positives, and false negatives. True negatives are not used for precision and recall, but they are not irrelevant.  The rate of true negatives affects accuracy and the higher it is, the more opportunity of false positives.

The terminology is straightforward for detection.  For correction it is somewhat confusing.  To illustrate, consider the possible classes of correction represented by the following
 tuples of (original, error, correction):

 (x,x,x) True Negative 

 (x,x,y) False Positive 

 (x,y,x) True Positive

 (x,y,y) False Negative

 (x,y,z) Detection True Positive, Correction False Negative *and* False Positive

For correction, we interpret recall to measure the proportion of all errors that were correctly corrected.  Since (x,y,z) is an error, and it is not correctly corrected, it is a false negative.  Precision measures the proportion of proposed corrections that were correctly corrected.  Since (x,y,z) has been corrected, but not correctly, it is also a false positive.

"""

xxy = 'False Positive'
xyx = 'True Positive'
xyy = 'False Negative'
xyz = 'Detection True Positive, Correction False Negative, Correction False Positive'

from collections import Counter

class CorrectionEvaluator():


    def __init__(self):

        self.detection_true_positives = 0
        self.correction_true_positives = 0
        self.detection_false_positives = 0
        self.correction_false_positives = 0
        self.detection_false_negatives = 0
        self.correction_false_negatives = 0

        self.distributions = {
            xxy : Counter(),
            xyx : Counter(),
            xyy : Counter(),
            xyz : Counter(),
            }

    def classify_correction_instance(self, original, error, observed, correction):

        assert original and error or not error
        assert observed and correction or not correction
        if original: assert original != error
        if observed: assert observed != correction
        if error and observed: assert observed == error

        if correction and not error: # xxy
            self.detection_false_positives += 1
            self.correction_false_positives += 1
            self.distributions[xxy][(observed, correction)] += 1
            return

        if correction:
            if correction == original: # xyx
                self.detection_true_positives += 1
                self.correction_true_positives += 1
                self.distributions[xyx][(observed, correction)] += 1
                return
                
            else: # xyz
                self.detection_true_positives += 1
                self.correction_false_negatives += 1
                self.correction_false_positives += 1
                self.distributions[xyz][(observed, original, correction)] +=1
                return

        else: # xyy
            assert error and not correction
            self.detection_false_negatives += 1
            self.correction_false_negatives += 1
            self.distributions[xyy][(error, original)] += 1
            return



if __name__ == '__main__':

    pass

