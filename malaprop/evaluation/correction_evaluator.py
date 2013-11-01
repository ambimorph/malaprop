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

from collections import Counter, deque
from recluse.utils import precision_recall_f_measure
import json

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

    def process_all_corrections(self, true_corrections_file, proposed_corrections_file):

        true_queue = deque()
        proposed_queue = deque()

        def parse_correction(correction):
            sentence_id = correction[0]
            result = []
            for c in correction[1]:
                token_id = c[0]
                subtoken_id = c[1]
                strings = c[2:]
                result.append(((sentence_id, token_id, subtoken_id), strings))
            return result

        def pop(f, q):

            try:
                next_item = q.popleft()
            except IndexError:
                line = f.readline()
                if line:
                    [q.append(c) for c in parse_correction(json.loads(line))]
                    next_item = q.popleft()
                else:
                    next_item = 'END'
            return next_item

        next_true = pop(true_corrections_file, true_queue)
        next_proposed = pop(proposed_corrections_file, proposed_queue)
        while not (next_true == 'END' or next_proposed == 'END'):
            error, original = next_true[1]
            observed, correction = next_proposed[1]
            if next_true[0] == next_proposed[0]:
                self.classify_correction_instance(original, error, observed, correction)
                next_true = pop(true_corrections_file, true_queue)
                next_proposed = pop(proposed_corrections_file, proposed_queue)
            elif next_true[0] < next_proposed[0]:
                self.classify_correction_instance(original, error, None, None)
                next_true = pop(true_corrections_file, true_queue)
            else:
                self.classify_correction_instance(None, None, observed, correction)
                next_proposed = pop(proposed_corrections_file, proposed_queue)
                
        while not next_true == 'END':
            error, original = next_true[1]
            self.classify_correction_instance(original, error, None, None)
            next_true = pop(true_corrections_file, true_queue)

        while not next_proposed == 'END':
            observed, correction = next_true[1]
            self.classify_correction_instance(None, None, observed, correction)
            next_proposed = pop(proposed_corrections_file, proposed_queue)

    def report(self, number_of_examples):

        result = {}

        result['Detection Precision'], result['Detection Recall'], result['Detection F-measure'] = \
            precision_recall_f_measure(self.detection_true_positives, self.detection_false_positives, self.detection_false_negatives)
        
        result['Correction Precision'], result['Correction Recall'], result['Correction F-measure'] = \
            precision_recall_f_measure(self.correction_true_positives, self.correction_false_positives, self.correction_false_negatives)

        for error in self.distributions.keys():
            result[error] = self.distributions[error].most_common(number_of_examples)

        return result


if __name__ == '__main__':

    pass

