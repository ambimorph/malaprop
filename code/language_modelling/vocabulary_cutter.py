# 2012 L. Amber Wilcox-O'Hearn

import sys, bisect

class VocabularyCutter():
    """
    Takes a file of unigram counts and returns a file of the top n most frequent words.
    """
    def __init__(self, infile_obj, outfile_obj):
        self.infile_obj = infile_obj
        self.outfile_obj = outfile_obj

    def cut_vocabulary(self, n):
        frequencies = []
        for line in self.infile_obj:
            tokens = line.split()
            assert len(tokens) == 2, line
            bisect.insort( frequencies, (int(tokens[1]), tokens[0]) )
        for i in range(n):
            self.outfile_obj.write(frequencies[-1-i][1])
            self.outfile_obj.write('\n')

if __name__ == '__main__':
    print sys.argv
    infile_obj = sys.stdin
    outfile_obj = sys.stdout
    vc = VocabularyCutter(infile_obj, outfile_obj)
    vc.cut_vocabulary(int(sys.argv[1]))
