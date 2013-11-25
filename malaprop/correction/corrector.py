# corrector.py

from malaprop.correction.HMM import *
from recluse.nltk_based_segmenter_tokeniser import *

def match_case(token_to_emulate, lowered_token):

    if token_to_emulate.istitle(): return lowered_token.title()
    if token_to_emulate.isupper(): return lowered_token.upper()
    if token_to_emulate.islower(): return lowered_token
    if token_to_emulate.lower() == lowered_token: return token_to_emulate
    if len(token_to_emulate) == len(lowered_token): 
        return ''.join([ lowered_token[i].upper() if i in [j for j in range(len(token_to_emulate)) if token_to_emulate[i].isupper()] else lowered_token[i] for i in range(len(lowered_token))])
    result = ''
    if len(token_to_emulate) < len(lowered_token):
        i = 0
        while i < len(token_to_emulate) and token_to_emulate.lower()[i] == lowered_token[i]:
            result += token_to_emulate[i]
            i += 1
        result += lowered_token[i] + token_to_emulate[i:]
        return result
                
    assert len(lowered_token) < len(token_to_emulate)
    i = 0
    while i < len(lowered_token) and token_to_emulate.lower()[i] == lowered_token[i]:
        result += token_to_emulate[i]
        i += 1
    result += token_to_emulate[i+1:]
    return result
                

class Corrector():

    def __init__(self, segmenter_tokeniser, hmm):

        self.segmenter_tokeniser = segmenter_tokeniser
        self.hmm = hmm

    def correct(self, sentence, output='corrections'):

        assert output in ['corrections', 'sentence']

        subtoken_list = [subtokenise(t, abbreviation_list=self.segmenter_tokeniser.sbd._params.abbrev_types) for t in sentence.split()]

        flat_subtokens = [subtoken for token in subtoken_list for subtoken in token]
        subtoken_count = len(flat_subtokens)

        flat_regular_subtokens = [regularise(subtoken.lower()) for subtoken in flat_subtokens]
        regularised_indices = [i for i in range(subtoken_count) if flat_regular_subtokens[i]!=flat_subtokens[i].lower()]

        flat_regular_correction = self.hmm.viterbi(flat_regular_subtokens)

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
