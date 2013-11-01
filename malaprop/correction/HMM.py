# HMM.py

from math import log10

class HMM():

    """
    This HMM is a model for spelling correction / text normalisation.

        States: a state represents the 'true' word at a given
        position.  That is, the intended word, or the normalised word
        type.  This means that the set of states is dependent on the observation.

        State transition probabilities will be the trigram
        probabilities of the state sequence.  That means we need to
        pass the backtraces.

        Emission probabilities depend on the set of variations of the
        word represented by the state, and the error rate (the
        probability that the observation is different from the 'true'
        word).
    """

    def __init__(self, confusion_set_function, trigram_probability_function, error_rate):

        self.confusion_set_function = confusion_set_function
        self.trigram_probability_function = trigram_probability_function
        self.error_rate = error_rate

    def viterbi(self, original_sentence, verbose=False):

        assert len(original_sentence) > 0
        sentence = original_sentence + ['</s>', '</s>']

        first_two_words = ['<s>', '<s>']
        variations = self.confusion_set_function(sentence[0])
        states = [sentence[0]] + variations
        observation_emission_probability = {var:log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations}
        observation_emission_probability[sentence[0]] = log10(1-self.error_rate)

        path_probabilities = [{('<s>', var): self.trigram_probability_function(first_two_words + [var]) + observation_emission_probability[var] for var in states}]
        backtrace = {('<s>', var):['<s>', var] for var in states}

        for position in range(1, len(sentence)):
            
            variations = self.confusion_set_function(sentence[position])
            states = [sentence[position]] + variations
            observation_emission_probability = {var:log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations}
            observation_emission_probability[sentence[position]] = log10(1-self.error_rate)

            path_probabilities.append({})
            new_backtrace = {}

            for var in states:
                probabilities_to_this_var = [(path_probabilities[position-1][prior_state] + self.trigram_probability_function(prior_state + (var,)) + observation_emission_probability[var], prior_state) for prior_state in path_probabilities[position-1].keys()]
                max_probability, max_prior_state = max(probabilities_to_this_var)
                path_probabilities[position][(max_prior_state[-1], var)] = max_probability
                new_backtrace[(max_prior_state[-1],var)] = backtrace[max_prior_state] + [var]
 
            backtrace = new_backtrace

        return backtrace[('</s>', '</s>')][1:-2]
