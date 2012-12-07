# 2012 L. Amber Wilcox-O'Hearn
# DamerauLevenshteinComputer.py

import codecs, unicodedata

class DamerauLevenshteinComputer():

    def __init__(self, vocabfile_obj=None, outfile_obj=None, maximum_distance=None):
        if vocabfile_obj is not None:
            self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        if outfile_obj is not None:
            self.unicode_outfile_obj = codecs.getwriter('utf-8')(outfile_obj)
        self.maximum_distance = maximum_distance

    #############################################################
    # The following function was created by Michael Homer,
    # and posted under the MIT license at 
    # http://mwh.geek.nz/2009/04/26/python-damerau-levenshtein-distance/
    # I have not modified it, except to add 'self'.

    def dameraulevenshtein(self, seq1, seq2):
        """Calculate the Damerau-Levenshtein distance between sequences.
    
        This distance is the number of additions, deletions, substitutions,
        and transpositions needed to transform the first sequence into the
        second. Although generally used with strings, any sequences of
        comparable objects will work.
    
        Transpositions are exchanges of *consecutive* characters; all other
        operations are self-explanatory.
    
        This implementation is O(N*M) time and O(M) space, for N and M the
        lengths of the two sequences.
    
        >>> dameraulevenshtein('ba', 'abc')
        2
        >>> dameraulevenshtein('fee', 'deed')
        2
    
        It works with arbitrary sequences too:
        >>> dameraulevenshtein('abcd', ['b', 'a', 'c', 'd', 'e'])
        2
        """
        # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
        # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
        # However, only the current and two previous rows are needed at once,
        # so we only store those.
        oneago = None
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in xrange(len(seq1)):
            # Python lists wrap around for negative indices, so put the
            # leftmost column at the *end* of the list. This matches with
            # the zero-indexed strings and saves extra calculation.
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in xrange(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
                # This block deals with transpositions
                if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                    and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                    thisrow[y] = min(thisrow[y], twoago[y - 2] + 1)
        return thisrow[len(seq2) - 1]
    #############################################################

    def compute_all_distances_from_vocab(self):
        assert 'unicode_vocabfile_obj' in dir(self)
        assert 'unicode_outfile_obj' in dir(self)
        previous_words = []
        for line in self.unicode_vocabfile_obj.readlines():
            word = line.strip()
            for previous_word in previous_words:
                distance = self.dameraulevenshtein(word, previous_word)
                if not self.maximum_distance or distance <= self.maximum_distance:
                    if word < previous_word:
                        self.unicode_outfile_obj.write(word + u' ' + previous_word + u' ' + unicode(self.dameraulevenshtein(word, previous_word)) + u'\n')
                    else:
                        self.unicode_outfile_obj.write(previous_word + ' ' + word + ' ' + str(self.dameraulevenshtein(word, previous_word)) + u'\n')
            previous_words.append(word)


if __name__ == '__main__':

    import sys
    dlc = DamerauLevenshteinComputer(sys.stdin, sys.stdout)
    dlc.compute_all_distances_from_vocab()
