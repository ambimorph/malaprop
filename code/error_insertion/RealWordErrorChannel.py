# 2012 L. Amber Wilcox-O'Hearn
# RealWordErrorChannel.py

from code.preprocessing import NLTKSegmentThenTokenise
import codecs, unicodedata, random, sys
from copy import deepcopy

class MidChannelToken():

    def __init__(self, token):
        # Results so far of passing prefix of the token through the channel:
        self.chars_passed = u''
        # Rest of the token not yet in the channel:
        self.remaining_chars = list(token) + [u'']
        # The channel has up to two chars in it for computing all
        # possible transformations:
        self.left_char = u''
        self.right_char = self.remaining_chars.pop(0)
        # The number of errors accumulated in this variation:
        self.number_of_errors = 0
        # Each error accumulated has a probability of happening which
        # is accumulated here to later be multiplied by the absolute
        # probability of error in the channel.
        self.error_probability_factor = 1
        # Similarly, the number of accumulated non-errors and
        # corresponding probability factor:
        self.number_of_non_errors = 0
        self.non_error_probability_factor = 1

    def __eq__(self, other):
        for attribute in [
            'chars_passed',
            'remaining_chars',
            'left_char',
            'right_char',
            'number_of_errors',
            'error_probability_factor',
            'number_of_non_errors',
            'non_error_probability_factor']:
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %r %r %r %r %d %d>' % (self.__class__.__name__, self.chars_passed, self.left_char, self.right_char, self.remaining_chars, self.number_of_errors, self.number_of_non_errors)

class RealWordErrorChannel():

    def __init__(self, segmenter_training_text_infile_obj, vocabfile_obj, outfile_obj, corrections_file_obj, p, random_number_generator):
        self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        self.unicode_outfile_obj = codecs.getwriter('utf-8')(outfile_obj)
        self.unicode_corrections_file_obj = codecs.getwriter('utf-8')(corrections_file_obj)
        self.real_words, self.symbols = self.get_real_words_and_symbols()
        self.segmenter_tokeniser = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(segmenter_training_text_infile_obj, outfile_obj)
        self.p = p
        self.random_number_generator = random_number_generator
        self.reset_stats()

    def reset_stats(self):
        self.real_word_errors = 0.0
        self.real_word_tokens_passed_through = 0.0
        self.mean_errors_per_word = 0.0
        self.max_errors_per_word = 0.0

    def get_stats(self):
        return self.real_word_errors, self.real_word_tokens_passed_through, self.mean_errors_per_word, self.max_errors_per_word
        
    
    def get_real_words_and_symbols(self):
        # Unicode-Read the vocab file 
        # For every item than contains letters and possibly periods and apostrophes
        # add item to real_words and symbols to symbols
        real_words = set([])
        symbols = set([])
        for line in self.unicode_vocabfile_obj.readlines():
            word = line.strip()
            real_words.add(word)
            symbols.update(set(word))

        symbols = list(symbols)
        return real_words, symbols
        
    def is_real_word(self, token):
        return token in self.real_words

    def create_error(self, left_char, right_char):
        assert not (left_char == u'' and right_char == u'')

        if left_char == u'': # No transposition
            possible_error_types = ["INSERTION", "DELETION", "SUBSTITUTION"]
        elif right_char == u'': # Insertion only
            possible_error_types = ["INSERTION"]
        else:
            possible_error_types = ["INSERTION", "DELETION", "SUBSTITUTION", "TRANSPOSITION"]

        if self.random_number_generator.random() < self.p: # create an error
            if possible_error_types == ["INSERTION"]:
                error_type = "INSERTION"
            else:
                error_type = self.random_number_generator.choice(possible_error_types)
        
            if error_type == "INSERTION":
                print "insertion!", left_char, right_char
                symbol_to_insert = self.random_number_generator.choice(self.symbols)
                return [left_char, symbol_to_insert, right_char]
            elif error_type == "DELETION":
                print "deletion!", left_char, right_char
                return [left_char]
            elif error_type == "SUBSTITUTION":
                print "substitution!", left_char, right_char
                symbol_to_sub = self.random_number_generator.choice(self.symbols[:self.symbols.index(right_char)] + self.symbols[self.symbols.index(right_char)+1:])
                return [left_char, symbol_to_sub]
            else:
                print "transposition!", left_char, right_char
                return [right_char, left_char]

        else:
            print "no error added!", left_char, right_char
            return [left_char, right_char]
                

    def create_all_possible_errors_and_probs(self, left_char, right_char):
        assert not (left_char == u'' and right_char == u'')

        list_of_string_error_factor_pairs = []

        if left_char == u'': # No transposition
            number_of_error_types = 3
        elif right_char == u'': # Insertion only
            number_of_error_types = 1
        else:
            number_of_error_types = 4

        for i in range(number_of_error_types):
            if i == 0: # insertions
                list_of_string_error_factor_pairs += [(left_char + s + right_char, 1.0/number_of_error_types*1.0/(len(self.symbols))) for s in self.symbols]
            elif i == 1: # deletions
                list_of_string_error_factor_pairs += [(left_char, 1.0/number_of_error_types)]
            elif i == 2: # substitutions
                list_of_string_error_factor_pairs += [(left_char + s, 1.0/number_of_error_types*1.0/(len(self.symbols)-1)) for s in self.symbols[:self.symbols.index(right_char)] + self.symbols[self.symbols.index(right_char)+1:]]
            else: # transpositions
                list_of_string_error_factor_pairs += [(right_char + left_char, 1.0/number_of_error_types)]

        return list_of_string_error_factor_pairs

    def push_one_char(self, mid_channel_token, with_probability_p=True):
        '''
        If with_probability_p, returns MidChannelToken with one of the
        possible errors according to channel probability p, else
        returns all possible MidChannelTokens that are continuations.
        '''

        if with_probability_p:
            new_mid_channel_token = deepcopy(mid_channel_token)
            
            temp = self.create_error(new_mid_channel_token.left_char, new_mid_channel_token.right_char)
            print "temp:", temp
            if temp == [new_mid_channel_token.left_char, new_mid_channel_token.right_char]:
                new_mid_channel_token.chars_passed += temp[0]
                new_mid_channel_token.left_char = temp[1]
                if len(new_mid_channel_token.remaining_chars) > 0:
                    new_mid_channel_token.right_char = new_mid_channel_token.remaining_chars.pop(0)

            else:
                new_mid_channel_token.number_of_errors += 1
                new_mid_channel_token.chars_passed += temp[0]
                if len(temp) > 1:
                    new_mid_channel_token.chars_passed += temp[1]
                if len(temp) == 3: # insertion happened
                    new_mid_channel_token.left_char = temp[2]
                else:
                    new_mid_channel_token.left_char = u''
                if len(new_mid_channel_token.remaining_chars) > 0:
                    new_mid_channel_token.right_char = new_mid_channel_token.remaining_chars.pop(0)
                else:
                    new_mid_channel_token.right_char = u''

            return new_mid_channel_token

    def pass_token_through_channel(self, token):
        # If token is a real word, pass each pair of chars through
        # insert_error, else return original if result is a real word,
        # return it (possibly re-uppering), else return original
        # Update real_word_errors, real_word_tokens_passed_through,
        # mean_errors_per_word, max_errors_per_word
        assert len(token) > 0, token
        if not self.is_real_word(token):
            return token

        mid_channel_token = MidChannelToken(token)
        while mid_channel_token.left_char + mid_channel_token.right_char != u'':
            print mid_channel_token
            mid_channel_token = self.push_one_char(mid_channel_token)

        if mid_channel_token.left_char == u'' and mid_channel_token.right_char == u'':
            print "HERE"

        self.real_word_tokens_passed_through += 1
        if self.is_real_word(mid_channel_token.chars_passed):
            if mid_channel_token.chars_passed != token: 
                self.mean_errors_per_word = (self.mean_errors_per_word * self.real_word_errors + mid_channel_token.number_of_errors) / (self.real_word_errors + 1)
                self.max_errors_per_word = max(self.max_errors_per_word, mid_channel_token.number_of_errors)
                self.real_word_errors += 1
            return mid_channel_token.chars_passed
        return token

    def create_all_real_word_variations(self, token, maximum_errors):
        '''
        This will be like passing a token through the channel, but it
        will be like a beam search.  At each iteration, we add to the
        new beam every possible next error for the items currently on
        the beam, plus the non-error of just passing the next char
        through.
        '''
        
        # Completed variations: either reached maximum_errors, or end
        # of token, and happened to be real words: Variations here
        # come with the number of errors and non-errors, and the
        # accumulated probability of each of those errors and
        # non-errors to be multiplied by the absolute probability of
        # error in the channel.
        complete_variations = []

        mid_channel_token = MidChannelToken(token)

        # The beam holds every possible variation in progress:
#        beam = [mid_channel_token]
#        while beam != []:
#            next_beam = []
#            for partial_variation in beam:
#                possible_continuations = self.push_one_char(partial_variation, with_probability_p=False)
#                for continuation in possible_continuations:
#                    if partial_variation.remaining_chars == []:
#                        complete_variations.append(partial_variation)
#                    elif partial_variation.number_of_errors == maximum_errors:
#                        partial_variation.chars_passed += partial_variation.left_char + \
#                            partial_variation.right_char + u''.join(partial_variation.remaining_chars)
#                        partial_variation.left_char = partial_variation.right_char = u''
#                        partial_variation.remaining_chars = []
        

    def pass_sentence_through_channel(self, (original, boundaries, substitutions)):
        # Use boundaries to find tokens
        # If there are no substitutions within the token, lowercase it and pass it through the channel.
        # If it is replaced, recase it if necessary
        # else just put original token.
        result = u''
        corrections = []
        substitution_indices = [sub[0] for sub in substitutions]
        tokens_containing_subs = []
        for sub_index in substitution_indices:
            if len(boundaries) == 0 or boundaries[0] > sub_index:
                tokens_containing_subs.append(0)
            else:
                tokens_containing_subs.append(max([x for x in boundaries if x <= sub_index]))
        last_boundary = 0
        for next_boundary in boundaries + [len(original)]:
            current_token = original[last_boundary:next_boundary]
            current_token_is_title = current_token.istitle()
            current_token_is_upper = current_token.isupper()
            if last_boundary in tokens_containing_subs:
                result += current_token
            else:
                passed_token = self.pass_token_through_channel(current_token)
                if passed_token == current_token:
                    result += passed_token
                else:
                    if current_token_is_title:
                        passed_token = passed_token.title()
                    elif current_token_is_upper:
                        passed_token = passed_token.upper()
                    result += passed_token
                    corrections.append((last_boundary, passed_token, current_token))
            last_boundary = next_boundary
            
        return result, corrections

    def pass_file_through_channel(self, text=None):
        assert text is None or isinstance(text, unicode), text
        if text == None: text = self.segmenter_tokeniser.text 

        sentence_info_generator = self.segmenter_tokeniser.segmented_and_tokenised(text, file_output=False)
        i = 0
        for sentence in sentence_info_generator:
            possibly_erroneous_sentence, corrections = self.pass_sentence_through_channel(sentence)
            self.unicode_outfile_obj.write(possibly_erroneous_sentence + u'\n')
            if corrections != []:
                self.unicode_corrections_file_obj.write(str(i) + ' ' + repr(corrections) + '\n')
            i += 1
        self.unicode_corrections_file_obj.write(repr(self.get_stats()))

if __name__ == '__main__':

    vocab_file_name, corrections_file_name, p, seed = sys.argv[1:]
    rwec = RealWordErrorChannel(sys.stdin, open(vocab_file_name, 'rb'), sys.stdout, open(corrections_file_name, 'wb'), float(p), random.Random(int(seed)))
    rwec.pass_file_through_channel()
