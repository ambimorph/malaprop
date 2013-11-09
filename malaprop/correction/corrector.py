# corrector.py

from malaprop.correction.HMM import *
from recluse.nltk_based_segmenter_tokeniser import *

def match_case(token_to_emulate, lowered_token):

    if token_to_emulate.istitle(): return lowered_token.title()
    if token_to_emulate.isupper(): return lowered_token.upper()
    return lowered_token

class Corrector():

    def __init__(self, segmenter_tokeniser, confusion_set_function, backoff_trigram_model_pipe, error_rate):

        self.segmenter_tokeniser = segmenter_tokeniser
        self.hmm = HMM(confusion_set_function, self.trigram_probability, error_rate)
        self.backoff_trigram_model_pipe = backoff_trigram_model_pipe

    def trigram_probability(self, three_words):

        """
        This is a little hack to use for now with BackOffTrigramModel
        and SRILM trigram models.

        The issue is that SRILM uses only one BOS and EOS marker for
        every level of language model.  The client is then expected to
        reduce the order of the query at the sentnce boundaries.  For
        example, using a trigram model to estimate the probability of
        the sentence "<s> It was . </s>", we use P(It|<s>) * P(was|<s>
        It) * P(.|It was) * P(</s>|.).

        However, BackOffTrigramModel does not currently support bigram
        queries.  Until it does, we will substitute "<last_token> </s>
        </s>" with "</s> last_token </s>".  Since nothing ever appears
        after </s>, this will always give us the second bigram.
        """

        if three_words[1] == '</s>':
            bigram_inducer = ('</s>', three_words[0], three_words[1])
            return self.backoff_trigram_model_pipe.trigram_probability(bigram_inducer)
        else:
            return self.backoff_trigram_model_pipe.trigram_probability(three_words)

    def correct(self, sentence, output='corrections'):

        assert output in ['corrections', 'sentence']

        subtoken_list = [subtokenise(t, abbreviation_list=self.segmenter_tokeniser.sbd._params.abbrev_types) for t in sentence.split()]

        flat_subtokens = [subtoken for token in subtoken_list for subtoken in token]
        subtoken_count = len(flat_subtokens)

        flat_regular_subtokens = [regularise(subtoken.lower()) for subtoken in flat_subtokens]
        regularised_indices = [i for i in range(subtoken_count) if flat_regular_subtokens[i]!=flat_subtokens[i].lower()]

        flat_regular_correction = self.hmm.viterbi(flat_regular_subtokens, verbose=False)

        flat_correction = []
        for i in range(subtoken_count):
            if i in regularised_indices:
                flat_correction.append([flat_subtokens[i], None])
            else:
                proposed = match_case(flat_subtokens[i], flat_regular_correction[i])
                if proposed == flat_subtokens[i]:
                    flat_correction.append([flat_subtokens[i], None])
                else:
                    flat_correction.append([proposed, [flat_subtokens[i], proposed]])
                                                 
        corrected_words = (c for c in flat_correction)
        structured_correction = []
        corrections = []
        for i in range(len(subtoken_list)):
            t = subtoken_list[i]
            structured_correction.append([])
            for j in range(len(t)):
                s = t[j]
                next_corrected_word = corrected_words.next()
                structured_correction[-1].append(next_corrected_word[0])
                if next_corrected_word[1] is not None:
                    corrections.append([i,j] + next_corrected_word[1])
                
        if output == 'corrections':
            return corrections
        return u' '.join([u''.join(subtoken) for subtoken in structured_correction])
