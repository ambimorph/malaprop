# adversarial_evaluator.py

def report_accuracy(key_file, proposed_file):

    proposed_line = proposed_file.readline()
    key_line = key_file.readline()[:len(proposed_line)]

    return 1.0 * sum([x==y for (x,y) in zip(key_line,proposed_line)]) / len(key_line)

def report_accuracy_and_errors(key_file, proposed_file, adversarial_file):

    proposed_line = proposed_file.readline()
    key_line = key_file.readline()[:len(proposed_line)]

    pairs = zip(key_line, proposed_line)
    correct = 0.0
    error_lines = []
    for pair in pairs:
        line = adversarial_file.readline()
        if pair[0] == pair[1]: correct +=1
        else: error_lines.append(line)

    return correct / len(key_line), error_lines
        
    
