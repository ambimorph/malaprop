# adversarial_evaluator.py

def report_accuracy(key_file, proposed_file):

    key_line = key_file.readline()
    proposed_line = proposed_file.readline()

    assert len(key_line) == len(proposed_line)

    return 1.0 * sum([x==y for (x,y) in zip(key_line,proposed_line)]) / len(key_line)
