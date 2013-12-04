# HMM.py

from math import log10
import bisect, sys

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

    def __init__(self, confusion_set_function, trigram_model_pipe, error_rate, viterbi_type, prune_to=None, simple_surprise=None, surprise_index=None, verbose=False):

        """
        error_rate, simple_surprise, and surprise_index are given in non-log form,
        trigram_model_pipe gives log forms.
        """

        self.confusion_set_function = confusion_set_function
        self.trigram_model_pipe = trigram_model_pipe
        self.error_rate = error_rate
        self.log_alpha = log10(1 - error_rate)
        if viterbi_type == 2:
            self.viterbi = self.viterbi_two
        elif viterbi_type == 3:
            self.viterbi =self.viterbi_three
        self.prune_to = prune_to
        assert simple_surprise is None or surprise_index is None
        self.anomaly_detection = (simple_surprise is not None or surprise_index is not None)
        if simple_surprise is not None:
            self.log_simple_surprise = log10(simple_surprise)
            self.surprise_threshold_met = self.simple_surprise_met
        if surprise_index is not None:
            self.log_surprise_index = log10(surprise_index)
            self.surprise_threshold_met = self.surprise_index_met
        self.verbose = verbose
        self.observation_emission_probabilities = {}

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

    def simple_surprise_met(self, trigram):

        return self.trigram_probability(trigram) >= self.log_simple_surprise

    def surprise_index_met(self, trigram):

        if trigram[1] == '</s>':
            surprise_threshold = self.trigram_model_pipe.unigram_backoff(trigram[0]) - self.log_surprise_index
        if self.trigram_model_pipe.in_bigrams(trigram[:2]):
            surprise_threshold = self.trigram_model_pipe.bigram_backoff(trigram[:2]) - self.log_surprise_index
        else:
            surprise_threshold = self.trigram_model_pipe.unigram_backoff(trigram[1]) - self.log_surprise_index
        return self.trigram_probability(trigram) >= surprise_threshold

    def viterbi_three(self, original_sentence):

        """
        For the trigram transitions, states have to be two words instead of one.
        """

        if self.verbose: sys.stdout.write('.')

        assert len(original_sentence) > 0
        sentence = original_sentence + ['</s>', '</s>']
        first_two_words = ('<s>', '<s>')

        if self.anomaly_detection and self.surprise_threshold_met(first_two_words + (sentence[0],)):
            variations = []
        else:
            variations = self.confusion_set_function(sentence[0])
        if self.verbose == 2: print 'variations', variations
        states = set([ ('<s>', v) for v in [sentence[0]] + variations ])
        if self.verbose == 2: print 'states', states

        """
        Building a cache of observation emission probabilities:
        a dict { observed : {variation : probability} }.
        """
        self.observation_emission_probabilities[sentence[0]] = { sentence[0] : log10(1-self.error_rate) }
        self.observation_emission_probabilities[sentence[0]].update( { var : log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations} )
        if self.verbose == 2: print 'observation_emission_probabilities', self.observation_emission_probabilities

        path_probabilities = [{}]
        path_probability_list = [ (self.trigram_probability(('<s>',) + state) + self.observation_emission_probabilities[sentence[0]][state[1]], state) for state in states ]
        path_probability_list.sort()
        for (p,s) in path_probability_list[-self.prune_to:]:
            path_probabilities[0][s] = p
        if self.verbose == 2: print 'path probabilities', path_probabilities
        backtrace = { state : (state[1],) for state in states }
        if self.verbose == 2: print 'backtrace', backtrace, '\n'

        def probability_to_this_state(position, state, prior_state):

            assert prior_state[1] == state[0]
            return path_probabilities[position-1][prior_state] + \
                self.trigram_probability((prior_state[0],) + state) + \
                self.observation_emission_probabilities[sentence[position]][state[1]]


        for position in range(1, len(sentence)):
            
            if self.verbose == 2: print 'Position %d, observed word: %s' % (position, sentence[position].encode('utf-8'))

            observed_word_trigram_probabilities = {}
            if sentence[position] in self.observation_emission_probabilities.keys():
                variations = [k for k in self.observation_emission_probabilities[sentence[position]].keys() if k != sentence[position]]
            else:
                self.observation_emission_probabilities[sentence[position]] = { sentence[position] : log10(1-self.error_rate) }
                variations = self.confusion_set_function(sentence[position])
                self.observation_emission_probabilities[sentence[position]].update( { var : log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations} )
            if self.verbose == 2: print 'observation_emission_probabilities', self.observation_emission_probabilities

            states = set([ (prior_state[-1], v) for v in [sentence[position]] + variations for prior_state in path_probabilities[position-1].keys()])
            if self.verbose == 2: print 'states', states, '\n'
            probabilities_to = { state:[] for state in states }
            if self.verbose == 2: print 'probabilities_to', probabilities_to

            for prior_state in path_probabilities[position-1].keys():

                if self.verbose == 2: print 'prior_state: ', prior_state

                observed_word_trigram_probabilities[prior_state] = self.trigram_probability(prior_state + (sentence[position],))

                # Get the probabilities to each variation if surprised by the observed.
                if not self.anomaly_detection or not self.surprise_threshold_met(prior_state + (sentence[position],)):
                    for state in states:
                        if prior_state[-1] == state[0]:
                            probabilities_to[state].append((probability_to_this_state(position, state, prior_state), prior_state))
                else:
                    # Always get the transitions to the observed word
                    probabilities_to[(prior_state[-1], sentence[position])].append( \
                    (probability_to_this_state(position, (prior_state[-1], sentence[position]), prior_state), prior_state))
                
            if self.verbose == 2: print 'probabilities_to', probabilities_to

            path_probability_list = []
            new_backtrace = {}

            for state in probabilities_to.keys():

                if probabilities_to[state] != []:
                    max_probability, max_prior_state = max(probabilities_to[state])
                    bisect.insort( path_probability_list, (max_probability, state) )
                    new_backtrace[state] = backtrace[max_prior_state] + (state[1],)
 
            path_probabilities.append({})
            for (p,s) in path_probability_list[-self.prune_to:]:
                path_probabilities[position][s] = p
            backtrace = new_backtrace
            if self.verbose == 2: 
                print 'backtrace', 
                for k,v in backtrace.iteritems(): print k,v
                print

        (final_probability, final_state) = max((path_probabilities[position][state], state) for state in states)
        return backtrace[final_state][:-2]

   ###################

    def viterbi_two(self, original_sentence):

        """
        Computes with trigram probabilities, but the states are only
        one word.  This corresponds to using only the first two
        trigrams for a given word.
        """
        if self.verbose: sys.stdout.write('.')

        assert len(original_sentence) > 0
        sentence = original_sentence + ['</s>', '</s>']

        first_two_words = ('<s>', '<s>')
        if self.anomaly_detection and self.surprise_threshold_met(first_two_words + (sentence[0],)):
            variations = []
        else:
            variations = self.confusion_set_function(sentence[0])
        states = [sentence[0]] + variations
        if self.verbose == 2: print 'variations, states:', variations, states

        """
        Building a cache of observation emission probabilities:
        a dict from (observed, var) to probability.
        """
        self.observation_emission_probabilities[sentence[0]] = { sentence[0] : log10(1-self.error_rate) }
        self.observation_emission_probabilities[sentence[0]].update( { var : log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations} )
        if self.verbose == 2: print 'observation_emission_probabilities', self.observation_emission_probabilities

        path_probabilities = [ {('<s>', state): self.trigram_probability(first_two_words + (state,)) + self.observation_emission_probabilities[sentence[0]][state] for state in states} ]
        backtrace = {('<s>', state):('<s>', state) for state in states}
        if self.verbose == 2: print 'path probabilities', path_probabilities, '\n'

        for position in range(1, len(sentence)):

            if self.verbose == 2: print 'Position %d, word %s' % (position, sentence[position].encode('utf-8'))

            observed_word_trigram_probabilities = {}
            if sentence[position] in self.observation_emission_probabilities.keys():
                variations = [k for k in self.observation_emission_probabilities[sentence[position]].keys() if k != sentence[position]]
            else: 
                self.observation_emission_probabilities[sentence[position]] = { sentence[position] : log10(1-self.error_rate) }
                variations = self.confusion_set_function(sentence[position])
                self.observation_emission_probabilities[sentence[position]].update( { var : log10(self.error_rate/len(self.confusion_set_function(var))) for var in variations} )
            if self.verbose == 2: print 'observation_emission_probabilities', self.observation_emission_probabilities

            probabilities_to = { var:[] for var in variations + [sentence[position]] }

            for prior_bigram in path_probabilities[position-1].keys():

                observed_word_trigram_probabilities[prior_bigram] = self.trigram_probability(prior_bigram + (sentence[position],))

                # Get the probabilities to each variation if surprised by the observed.
                if not self.anomaly_detection or not self.surprise_threshold_met(prior_bigram + (sentence[position],)):
                    for var in variations + [sentence[position]]:
                        probabilities_to[var].append( (path_probabilities[position-1][prior_bigram] + \
                                                            self.trigram_probability(prior_bigram + (var,)) +\
                                                            self.observation_emission_probabilities[sentence[position]][var], prior_bigram) )
                else:
                    if self.verbose == 2 and self.anomaly_detection:
                        print 'surprise!', prior_bigram, sentence[position], observed_word_trigram_probabilities[prior_bigram]

                    # Always get the transitions to the observed word
                    probabilities_to[sentence[position]].append( (path_probabilities[position-1][prior_bigram] + \
                                                                      observed_word_trigram_probabilities[prior_bigram] + \
                                                                      self.observation_emission_probabilities[sentence[position]][sentence[position]], prior_bigram) )

            if self.verbose == 2: print 'probabilities_to', probabilities_to

            path_probabilities.append({})
            new_backtrace = {}
            for var in probabilities_to.keys():

                if probabilities_to[var] != []:
                    max_probability, max_prior_bigram = max(probabilities_to[var])
                    path_probabilities[position][(max_prior_bigram[-1], var)] = max_probability
                    new_backtrace[(max_prior_bigram[-1],var)] = backtrace[max_prior_bigram] + (var,)

            if self.verbose == 2: print 'new_backtrace ', new_backtrace
            if self.verbose == 2: print 'path probabilities', path_probabilities, '\n'

            backtrace = new_backtrace

        return backtrace[('</s>', '</s>')][1:-2]
