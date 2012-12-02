# 2012 L. Amber Wilcox-O'Hearn
# RealWordErrorChannel.py

import NLTKSegmentThenTokenise
import codecs, unicodedata, random, sys

class RealWordErrorChannel():

    def __init__(self, segmenter_training_text_infile_obj, vocabfile_obj, outfile_obj, p, random_number_generator):
        self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        self.unicode_outfile_obj = codecs.getreader('utf-8')(outfile_obj)
        self.real_words, self.symbols = self.get_real_words_and_symbols()
        self.segmenter_tokeniser = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(segmenter_training_text_infile_obj, outfile_obj)
        self.p = p
        self.random_number_generator = random_number_generator
        self.reset_stats()

    def reset_stats(self):
        self.real_word_errors = 0.0
        self.real_word_tokens_passed_though = 0.0
        self.mean_errors_per_word = 0.0
        self.max_errors_per_word = 0.0
        
    
    def get_real_words_and_symbols(self):
        # Unicode-Read the vocab file 
        # For every item than contains letters and possibly periods and apostrophes
        # add item to real_words and symbols to symbols
        real_words = set([])
        symbols = set([])
        for line in self.unicode_vocabfile_obj.readlines():
            word = line.strip()
            contains_letters = False
            real_word = True
            for char in word:
                if unicodedata.category(char)[0] == 'L':
                    contains_letters = True
                elif char != u'.' and char != u"'":
                    real_word = False
                    break
            if not contains_letters: real_word = False
            if real_word:
                real_words.add(word)
                symbols.update(set(word))

        symbols = list(symbols)
        return real_words, symbols
        
    def is_real_word(self, token):
        return token in self.real_words

    def create_error_with_probability_p(self, left_char, right_char, p=None, random_number_generator=None):
        assert not (left_char == u'' and right_char == u'')
        if p == None: p = self.p
        if random_number_generator == None: random_number_generator = self.random_number_generator
        assert type(random_number_generator) is random.Random, random_number_generator

        if random_number_generator.random() < p: # create an error
            # 0 = Insertion, 1 = Deletion, 2 = Substitution, 3 = Transposition

            if left_char == u'': # No transposition
                error_type = random_number_generator.randrange(3)
            elif right_char == u'': # Insertion only
                error_type = 0
            else:
                error_type = random_number_generator.randrange(4)
            
            if error_type == 0: # print "insertion!"
                symbol_to_insert = random_number_generator.choice(self.symbols)
                return left_char + symbol_to_insert + right_char
            elif error_type == 1: # print "deletion!"
                return left_char
            elif error_type == 2: # print "substitution!"
                symbol_to_sub = random_number_generator.choice(self.symbols)
                return left_char + symbol_to_sub
            else: # print "transposition!"
                return right_char + left_char
            
        else: # print "no error added!"
            return left_char + right_char

    def pass_token_through_channel(self, token, random_number_generator=None):
        # If token is a real word, pass each pair of chars through insert_error, else return original
        # if result is a real word, return it (possibly re-uppering), else return original
        # Update real_word_errors, real_word_tokens_passed_though, mean_errors_per_word, max_errors_per_word
        if random_number_generator == None: random_number_generator = self.random_number_generator
        assert type(random_number_generator) is random.Random, random_number_generator
        assert len(token) > 0, token
        if not self.is_real_word(token):
            return token
        result = u''
        number_of_errors_so_far = 0
        remaining_chars = list(token) + [u'']
        left_char = u''
        right_char = remaining_chars.pop(0)
        while len(remaining_chars) > 0:
            temp = self.create_error_with_probability_p(left_char, right_char, random_number_generator=random_number_generator)
            if temp != left_char + right_char: number_of_errors_so_far += 1
            if len(temp) == 1:
                left_char = temp
                right_char = remaining_chars.pop(0)
            elif len(temp) == 2:
                result += temp[0]
                left_char = temp[1]
                right_char = remaining_chars.pop(0)
            elif len(temp) == 3:
                result += temp[0]
                left_char = temp[1]
                right_char = temp[2]

        temp = self.create_error_with_probability_p(left_char, right_char, random_number_generator=random_number_generator)
        if temp != left_char + right_char: number_of_errors_so_far += 1
        while len(temp) == 2:
            result += temp[0]
            left_char = temp[1]
            right_char = u''
            temp = self.create_error_with_probability_p(left_char, right_char, random_number_generator=random_number_generator)
            if temp != left_char + right_char: number_of_errors_so_far += 1

        result += temp
        self.real_word_tokens_passed_though += 1
        if self.is_real_word(result):
            if result != token: 
                self.mean_errors_per_word = (self.mean_errors_per_word * self.real_word_errors + number_of_errors_so_far) / (self.real_word_errors + 1)
                self.max_errors_per_word = max(self.max_errors_per_word, number_of_errors_so_far)
                self.real_word_errors += 1
            return result
        return token

    def pass_sentence_through_channel(self, (original, boundaries, substitutions), random_number_generator=None):
        # Use boundaries to find tokens
        # If there are no substitutions within the token, lowercase it and pass it through the channel.
        # If it is replaced, recase it if necessary
        # else just put original token.
        if random_number_generator == None: random_number_generator = self.random_number_generator
        assert type(random_number_generator) is random.Random, random_number_generator
        result = u''
        substitution_indices = [sub[0] for sub in substitutions]
        tokens_containing_subs = []
        for sub_index in substitution_indices:
            if boundaries[0] > sub_index:
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
                passed_token = self.pass_token_through_channel(current_token, random_number_generator=random_number_generator)
                if passed_token == current_token:
                    result += passed_token
                elif current_token_is_title:
                    result += passed_token.title()
                elif current_token_is_upper:
                    result += passed_token.upper()
                else:
                    result += passed_token
            last_boundary = next_boundary
            
        return result

    def pass_file_through_channel(self, text=None, random_number_generator=None):
        assert text is None or isinstance(text, unicode), text
        if text == None: text = self.text 
        if random_number_generator == None: random_number_generator = self.random_number_generator
        assert type(random_number_generator) is random.Random, random_number_generator

        sentence_info_generator = self.segmenter_tokeniser.segmented_and_tokenised(text, file_output=False)
        for sentence in sentence_info_generator:
            possibly_erroneous_sentence = self.pass_sentence_through_channel(sentence, random_number_generator=random_number_generator)
            self.unicode_outfile_obj.write(possibly_erroneous_sentence + u'\n')

        if self.real_word_tokens_passed_though == 0: 
            return ( -1, self.mean_errors_per_word, self.max_errors_per_word )
        return ( self.real_word_errors * 1.0 / self.real_word_tokens_passed_though, self.mean_errors_per_word, self.max_errors_per_word )

if __name__ == '__main__':

    vocab_file_name, p, seed = sys.argv[1:]
    rwec = RealWordErrorChannel(sys.stdin, sys.stdout)
    rwec.pass_file_through_channel()
