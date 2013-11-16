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

        variations = self.confusion_set_function(sentence[0])
        if verbose: print 'variations', variations
        states = [ ('<s>', '<s>', v) for v in [sentence[0]] + variations ]
        observation_emission_probability = { state : log10(self.error_rate/len(self.confusion_set_function(state[2]))) for state in states if state[2] != sentence[0] }
        observation_emission_probability.update( { state : log10(1-self.error_rate) for state in states if state[2] == sentence[0] } )
        path_probabilities = [ { state : self.trigram_probability_function(state) + observation_emission_probability[state] for state in states } ]
        backtrace = { state : (state[2],) for state in states }
        if verbose: print 'path probabilities', path_probabilities

        for position in range(1, len(sentence)):
            
            if verbose: print "Position %d" % position
            variations = self.confusion_set_function(sentence[position])
            if verbose: print 'variations of ', sentence[position], variations
            states = [ (prior_state[-2], prior_state[-1], v) for v in [sentence[position]] + variations for prior_state in path_probabilities[position-1].keys()]
            observation_emission_probability = { state : log10(self.error_rate/len(self.confusion_set_function(state[2]))) if state[2] != sentence[position] \
                                                     else log10(1-self.error_rate) for state in states }
            path_probabilities.append({})
            new_backtrace = {}

            for state in states:

                probabilities_to_this_state = [(path_probabilities[position-1][prior_state] + \
                                                    self.trigram_probability_function(state) + \
                                                    observation_emission_probability[state], 
                                                prior_state) \
                                                   for prior_state in path_probabilities[position-1].keys() \
                                                   if (prior_state[-2], prior_state[-1]) == (state[0], state[1])]

                max_probability, max_prior_state = max(probabilities_to_this_state)
                if verbose: print max_probability, max_prior_state
                path_probabilities[position][state] = max_probability
                if verbose: print 'path probabilities', path_probabilities
                new_backtrace[state] = backtrace[max_prior_state] + (state[2],)
 
            backtrace = new_backtrace

        (final_probability, final_state) = max((path_probabilities[position][states], states) for states in states)
        return backtrace[final_state][:-2]
