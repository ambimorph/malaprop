# 2012 L. Amber Wilcox-O'Hearn
# RealWordErrorChannel.py

import NLTKSegmentThenTokenise
import codecs, unicodedata

class RealWordErrorChannel():

    def __init__(self, segmenter_training_text_infile_obj, vocabfile_obj, outfile_obj, p, random_number_generator):
        self.unicode_vocabfile_obj = codecs.getreader('utf-8')(vocabfile_obj)
        self.real_words, self.symbols = self.get_real_words_and_symbols()
        # Pass infile through NLTKSegmentThenTokenise to train
        self.p = p
        self.random_number_generator = random_number_generator
        self.real_word_errors = 0
        self.real_word_tokens_passed_though = 0
        self.mean_errors_per_word = 0
        self.max_errors_per_word = 0
    
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
        assert left_char != u'' or right_char != u''
        if p == None: p = self.p
        if random_number_generator == None: random_number_generator = self.random_number_generator

        if random_number_generator.random() < p: # create an error
            # 0 = Insertion, 1 = Deletion, 2 = Substitution, 3 = Transposition

            if left_char == u'': # No transposition
                error_type = random_number_generator.randrange(3)
            elif right_char == u'': # Insertion only
                error_type = 0
            else:
                error_type = random_number_generator.randrange(4)
            
            if error_type == 0: # "insertion!"
                return left_char + random_number_generator.choice(self.symbols) + right_char, True
            elif error_type == 1: # "deletion!"
                return left_char, True
            elif error_type == 2: # "substitution!"
                return left_char + random_number_generator.choice(self.symbols), True
            else: # "transposition!"
                return right_char + left_char, True
            
        else:
            return left_char + right_char, False

    def pass_token_through_channel(self, token, random_number_generator=None):
        # If token is a real word, pass each pair of chars through insert_error, else return original
        # if result is a real word, return it (possibly re-uppering), else return original
        # Update real_word_errors, real_word_tokens_passed_though, mean_errors_per_word, max_errors_per_word
        if random_number_generator == None: random_number_generator = self.random_number_generator
        result = u''
        end_of_buffer_position = 1

        left = 0
        
        return result

    def pass_sentence_through_channel(self, (original, boundaries, substitutions), random_number_generator=None):
        # Use boundaries to find tokens
        # If there are no substitutions within the token, pass it through the channel first,
        # else just write it out.
        if random_number_generator == None: random_number_generator = self.random_number_generator

    def pass_file_through_channel(self, text=None, random_number_generator=None):
        assert text is None or isinstance(text, unicode), text
        if text == None: text = self.text # change this to say unicode-read training text
        if random_number_generator == None: random_number_generator = self.random_number_generator
        # Put through Segmenter_tokeniser
        # For sentence in segmenter_tokeniser output,
        # pass sentence through channel.
        # Write result to unicode_outfile
        # return statistics
        if self.real_word_tokens_passed_though == 0: 
            return ( -1, self.mean_errors_per_word, self.max_errors_per_word )
        return ( self.real_word_errors * 1.0 / self.real_word_tokens_passed_though, self.mean_errors_per_word, self.max_errors_per_word )

if __name__ == '__main__':

    rwec = RealWordErrorChannel(sys.stdin, sys.stdout)
