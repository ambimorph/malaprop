# HMM.py

from math import log10
import bisect

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

    def __init__(self, confusion_set_function, trigram_model_pipe, error_rate, viterbi_type, prune_to=None, surprise_index=None):

        """
        error_rate and surprise_index are given in non-log form,
        trigram_model_pipe gives log forms.
        """

        self.confusion_set_function = confusion_set_function
        self.trigram_model_pipe = trigram_model_pipe
        self.error_rate = error_rate
        if viterbi_type == 2:
            self.viterbi = self.viterbi_two
        elif viterbi_type == 3:
            self.viterbi =self.viterbi_three
        self.prune_to = prune_to
        if surprise_index is None:
            self.surprise_index = surprise_index
        else:
            self.surprise_index = log10(surprise_index)

    def trigram_probability(self, three_words):

        """
        This is a little hack to use for now with BackOffTrigramModel
        and SRILM trigram models.

        The issue is that SRILM uses only one BOS and EOS marker for
        every level of language model.  The client is then expected to
        reduce the order of the query at the sentence boundaries.  For
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
            return self.trigram_model_pipe.trigram_probability(bigram_inducer)
        else:
            return self.trigram_model_pipe.trigram_probability(three_words)

    def surprise_threshold_function(self, three_words):

        if three_words[1] == '</s>':
            surprise_threshold = self.trigram_model_pipe.unigram_backoff(three_words[0]) - self.surprise_index
        if self.trigram_model_pipe.in_bigrams(three_words[:2]):
            surprise_threshold = self.trigram_model_pipe.bigram_backoff(three_words[:2]) - self.surprise_index
        else:
            surprise_threshold = self.trigram_model_pipe.unigram_backoff(three_words[1]) - self.surprise_index
        return surprise_threshold

    def viterbi_three(self, original_sentence, verbose=False):

        """
        For the trigram transitions, states have to be two words instead of one.
        """
        if verbose: print '.'

        assert len(original_sentence) > 0
        sentence = original_sentence + ['</s>', '</s>']

        variations = self.confusion_set_function(sentence[0])
        if verbose == 2: print 'variations', variations
        states = set([ ('<s>', v) for v in [sentence[0]] + variations ])
        if verbose == 2: print 'states', states
        observation_emission_probability = { state : log10(self.error_rate/len(self.confusion_set_function(state[1]))) for state in states if state[1] != sentence[0] }
        observation_emission_probability.update( { state : log10(1-self.error_rate) for state in states if state[1] == sentence[0] } )
        if verbose == 2: print 'observation_emission_probability', observation_emission_probability
        path_probabilities = [ { state : self.trigram_probability(('<s>',) + state) + observation_emission_probability[state] for state in states } ]
        if verbose == 2: print 'path probabilities', path_probabilities
        backtrace = { state : (state[1],) for state in states }
        if verbose == 2: print 'backtrace', backtrace, '\n'

        for position in range(1, len(sentence)):
            
            if verbose == 2: print "Position %d" % position
            variations = self.confusion_set_function(sentence[position])
            if verbose == 2: print 'variations of ', sentence[position].encode('utf-8'), 
            if verbose == 2: print variations
            states = set([ (prior_state[-1], v) for v in [sentence[position]] + variations for prior_state in path_probabilities[position-1].keys()])
            if verbose == 2: print 'states', states, '\n'
            observation_emission_probability = { state : log10(self.error_rate/len(self.confusion_set_function(state[1]))) if state[1] != sentence[position] \
                                                     else log10(1-self.error_rate) for state in states }
            path_probabilities.append({})
            new_backtrace = {}

            path_probability_list = []
            for state in states:

                if verbose == 2: print 'state', state
                probabilities_to_this_state = [(path_probabilities[position-1][prior_state] + \
                                                    self.trigram_probability((prior_state[-1],) + state) + \
                                                    observation_emission_probability[state], prior_state) \
                                                   for prior_state in path_probabilities[position-1].keys() \
                                                   if prior_state[-1] == state[0]]

                max_probability, max_prior_state = max(probabilities_to_this_state)
                bisect.insort( path_probability_list, (max_probability, state) )
                path_probabilities[position][state] = max_probability
                if verbose == 2: print 'path probability to this state', path_probabilities[position][state]
                if verbose == 2: print 'Max probability to state, from', max_probability, max_prior_state,'\n'
                new_backtrace[state] = backtrace[max_prior_state] + (state[1],)
 
            for (p,s) in path_probability_list[-self.prune_to:]:
                path_probabilities[position][s] = p
            backtrace = new_backtrace
            if verbose == 2: 
                print 'backtrace', 
                for k,v in backtrace.iteritems(): print k,v
                print

        (final_probability, final_state) = max((path_probabilities[position][state], state) for state in states)
        return backtrace[final_state][:-2]

   ###################

    def viterbi_two(self, original_sentence, verbose=False):

        """
        Computes with trigram probabilities, but the states are only
        one word.  This corresponds to using only the first two
        trigrams for a given word.
        """
        if verbose: print '.'

        assert len(original_sentence) > 0
        sentence = original_sentence + ['</s>', '</s>']

        first_two_words = ('<s>', '<s>')
        if self.surprise_index is None or self.trigram_probability(first_two_words + (sentence[0],)) < self.surprise_threshold_function(first_two_words + (sentence[0],)):
            states = set([sentence[0]] + self.confusion_set_function(sentence[0]))
        else:
            states = set([sentence[0]])
        if verbose == 2: print 'states', states
        observation_emission_probability = { state : log10(self.error_rate/len(self.confusion_set_function(state))) if state != sentence[0] else log10(1-self.error_rate) for state in states }
        path_probabilities = [ {('<s>', state): self.trigram_probability(first_two_words + (state,)) + observation_emission_probability[state] for state in states} ]
        backtrace = {('<s>', state):('<s>', state) for state in states}
        if verbose == 2: print 'path probabilities', path_probabilities, '\n'

        for position in range(1, len(sentence)):

            if verbose == 2: print 'Position %d, word %s' % (position, sentence[position])
            
            suspicious_prior_bigrams = []
            for prior_bigram in path_probabilities[position-1].keys():
                if self.surprise_index is None or self.trigram_probability(prior_bigram + (sentence[position],)) < self.surprise_threshold_function(prior_bigram + (sentence[position],)):
                    suspicious_prior_bigrams.append(prior_bigram)
            if suspicious_prior_bigrams == []:
                variations = []
            else:
                variations = self.confusion_set_function(sentence[position])
            if verbose == 2: print 'variations', variations
            observation_emission_probability = { sentence[position] : log10(1-self.error_rate) }
            observation_emission_probability.update({ var : log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations })
                    

            path_probabilities.append({})
            new_backtrace = {}

            # Always get the transitions to the observed word
            probabilities_to_observed = [(path_probabilities[position-1][prior_bigram] + self.trigram_probability(prior_bigram + (sentence[position],)) + observation_emission_probability[sentence[position]], prior_bigram) for prior_bigram in path_probabilities[position-1].keys()]
            max_probability, max_prior_bigram = max(probabilities_to_observed)
            path_probabilities[position][(max_prior_bigram[-1], sentence[position])] = max_probability
            new_backtrace[(max_prior_bigram[-1], sentence[position])] = backtrace[max_prior_bigram] + ( sentence[position],)

            # Get the transitions to variations
            for var in variations:
                probabilities_to_this_var = [(path_probabilities[position-1][prior_bigram] + self.trigram_probability(prior_bigram + (var,)) + observation_emission_probability[var], prior_bigram) for prior_bigram in suspicious_prior_bigrams]
                max_probability, max_prior_bigram = max(probabilities_to_this_var)
                path_probabilities[position][(max_prior_bigram[-1], var)] = max_probability
                new_backtrace[(max_prior_bigram[-1],var)] = backtrace[max_prior_bigram] + (var,)
 
            backtrace = new_backtrace

        if verbose == 2: print 'path probabilities', path_probabilities, '\n'
        return backtrace[('</s>', '</s>')][1:-2]
