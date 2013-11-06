# trigram_based_chooser.py

from recluse.nltk_based_segmenter_tokeniser import *

class TrigramBasedChooser():

    def __init__(self, segmenter_tokeniser, trigram_probability_function):

        self.segmenter_tokeniser= segmenter_tokeniser
        self.trigram_probability_function = trigram_probability_function

    def sentence_probability(self, tokens):

        probability = 0
        bounded_tokens = ['<s>', '<s>'] + tokens + ['</s>']
        for i in range(len(tokens)+1):
            probability += self.trigram_probability_function(bounded_tokens[i:i+3])
        # Hack to deal with trigram-only interface -- forces backoff to second bigram:
        probability += self.trigram_probability_function(['</s>'] + bounded_tokens[-2:])
        return probability
                                                             

    def choose(self, pair):

        s0 = sentence_tokenise_and_regularise(pair[0].lower().split(), abbreviation_list=self.segmenter_tokeniser.sbd._params.abbrev_types).split()
        s1 = sentence_tokenise_and_regularise(pair[1].lower().split(), abbreviation_list=self.segmenter_tokeniser.sbd._params.abbrev_types).split()

        probabilities = [self.sentence_probability(s) for s in [s0, s1]]
        return probabilities.index(max(probabilities))
