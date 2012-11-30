# 2012 L. Amber Wilcox-O'Hearn
# NLTKSegmentThenTokenise.py

import nltk
import re, sys, codecs, unicodedata, string

class NLTKSegmenterPlusTokeniser():

    def __init__(self, infile_obj, outfile_obj):
        self.unicode_infile_obj = codecs.getreader('utf-8')(infile_obj)
        self.text = self.unicode_infile_obj.read()
        self.unicode_outfile_obj = codecs.getwriter('utf-8')(outfile_obj)
        trainer = nltk.tokenize.punkt.PunktTrainer()
        trainer.ABBREV = .15
        trainer.IGNORE_ABBREV_PENALTY = True
        trainer.INCLUDE_ALL_COLLOCS = True
        trainer.MIN_COLLOC_FREQ = 10
        trainer.train(self.text)
        self.sbd = nltk.tokenize.punkt.PunktSentenceTokenizer(trainer.get_params())

    def is_an_initial(self, word):
        if len(word) == 2 and unicodedata.category(word[0])[0] == 'L' and word[1] == u'.':
            return True
        return False
    def multi_char_word_and_starts_with_a_capital(self, word):
        if len(word) > 1 and unicodedata.category(word[0]) == 'Lu':
            return True
        return False

    def apply_ugly_hack_to_reattach_wrong_splits_in_certain_cases_with_initials(self, lines):
        # NLTK currently splits sentences between 2 initials.  Hacking those back together.
        # Also has the effect of collapsing whitespace to a single space char.
        lines = list(lines)
        if len(lines) == 0: return []
        reattached_lines = []
        i = 0
        current_line = lines[i].split()
        while i < len(lines) - 1:
            reattach = False
            next_line = lines[i+1].split()
            last_word = current_line[-1]
            next_line_starts_with_a_capital = False
            first_word_of_next_line = next_line[0]
            if len(first_word_of_next_line) > 1 and unicodedata.category(first_word_of_next_line[0]) == 'Lu':
                next_line_starts_with_a_capital = True
            if self.is_an_initial(last_word):
                nltk_ortho_context = self.sbd._params.ortho_context[first_word_of_next_line.lower()]
                if unicodedata.category(first_word_of_next_line[0])[0] != 'L':
                    reattach = True
                # The following is an ugly and imperfect hack.  See mailing list for nltk.
                elif self.multi_char_word_and_starts_with_a_capital(first_word_of_next_line) and \
                        nltk_ortho_context <= 46 or \
                        self.is_an_initial(first_word_of_next_line):
                    reattach = True

            if reattach:
                    current_line += next_line
            else:
                reattached_lines.append(u' '.join(current_line))
                current_line = next_line
            i += 1 
        reattached_lines.append(u' '.join(current_line))
        return reattached_lines
                
    def lists_of_internal_token_boundaries_and_special_tokens(self, line):
        # If any chars are unicode punctuation and not periods, put boundary marks around them
        # except at the beginning and end of the line, and unless it is a
        # contraction or an inter-numeric comma.
        # Also put boundaries around ellipses.
        # Strings of digits are listed in the substitutions list with '<n-digit-integer>'
        # I've traded some readability for doing it in one pass.

        boundaries_set = set([])
        special_tokens = []
        digit_length = 0
        number_punct = False
        if unicodedata.category(line[0]) == 'Nd':
            digit_length = 1
        elif unicodedata.category(line[0])[0] in 'PS' and line[0] != '.':
            boundaries_set.add(1)
        for i in [x+1 for x in range(len(line)-1)]:
            if unicodedata.category(line[i]) == 'Nd':
                # We're in a digit string.
                digit_length += 1
            else:
                if digit_length > 0:
                    # Either there is a period or comma in the digit string or
                    # this ends the digit string. 
                    if (line[i] == '.' or line[i] == ',') and i < len(line)-1 and unicodedata.category(line[i+1]) =='Nd':
                        number_punct = True
                    special_tokens.append( (i - digit_length, digit_length,  u'<' + unicode(str(digit_length)) + u'-digit-integer>') )
                    digit_length = 0
                if unicodedata.category(line[i])[0] in 'PSZ' and line[i] != '.' and not number_punct:
                    if (line[i] == '\'' or line[i] == u'\xb4') and unicodedata.category(line[i-1])[0] == 'L' \
                        and i < len(line)-1 and unicodedata.category(line[i+1])[0] == 'L':
                        pass
                    else:
                        boundaries_set.update([i, i+1])
                number_punct = False
        if digit_length != 0:
            special_tokens.append( (len(line) - digit_length, digit_length,  u'<' + unicode(str(digit_length)) + u'-digit-integer>') )
            
        # Mark a boundary before sentence-final period if not an abbrevation
        i = len(line) - 1
        while unicodedata.category(line[i])[0] not in 'LN' and i >= 0:
            i -= 1
        if i >= 0:
            if i != len(line) - 1 and line[i+1] == '.':
                period_index = i+1
                # See if preceding token is an abbreviation or initial.
                while unicodedata.category(line[i]) != 'Zs' and i >= 0:
                    i -= 1
                token_index = i+1
                abbreviations = self.sbd._params.abbrev_types
                if line[token_index:period_index].lower() not in abbreviations and \
                        not (token_index + 1 == period_index and unicodedata.category(line[token_index]) == 'Lu'):
                    boundaries_set.add(period_index)

        # Find ellipses
        ellipses_index = line.find(u'...')
        while ellipses_index != -1:
            boundaries_set.add(ellipses_index)
            ellipses_index = line.find(u'...', ellipses_index+1)

        boundaries_set.discard(len(line))
        boundaries = list(boundaries_set)
        boundaries.sort()
        return boundaries, special_tokens

    def tokenised_text(self, sentence_and_token_information):

        text, boundaries, substitutions = sentence_and_token_information
        current_index = 0
        result = u''
        if len(boundaries) == 0: next_boundary = None
        else: 
            next_boundary_index = 0
            next_boundary = boundaries[0]
        if len(substitutions) == 0: next_sub = None
        else: 
            next_sub_index = 0
            next_sub, sub_length, sub_text = substitutions[0]

        while next_boundary is not None or next_sub is not None:
            while next_boundary is not None and (next_sub is None or next_boundary < next_sub):
                result += text[current_index:next_boundary] + u' '
                current_index = next_boundary
                next_boundary_index += 1
                if len(boundaries) < next_boundary_index + 1:
                    next_boundary = None
                else:
                    next_boundary = boundaries[next_boundary_index]
                if next_boundary is None and next_sub is None:
                    result += text[current_index:]
               
            if next_boundary is not None and next_sub is not None and next_boundary == next_sub:
                result += text[current_index:next_boundary] + u' ' + sub_text
                current_index = next_sub + sub_length
                next_boundary_index += 1
                if len(boundaries) < next_boundary_index + 1:
                    next_boundary = None
                else:
                    next_boundary = boundaries[next_boundary_index]
                next_sub_index += 1
                if len(substitutions) < next_sub_index + 1:
                    next_sub = None
                else:
                    next_sub, sub_length, sub_text = substitutions[next_sub_index]
                
            while next_sub is not None and (next_boundary is None or next_sub < next_boundary):
                result += text[current_index:next_sub] + sub_text
                current_index = next_sub + sub_length
                next_sub_index += 1
                if len(substitutions) < next_sub_index + 1:
                    next_sub = None
                else:
                    next_sub, sub_length, sub_text = substitutions[next_sub_index]
        return result
           
                    

    def segmented_and_tokenised(self, text=None, file_output=True):
        assert text is None or isinstance(text, unicode), text
        if text == None: text = self.text
        for line in (t for t in text.split('\n')):
            sentences = self.sbd.sentences_from_text(line, realign_boundaries=True)
            sentences = self.apply_ugly_hack_to_reattach_wrong_splits_in_certain_cases_with_initials(sentences)
            for sentence in sentences:
                sentence_and_token_information = (sentence,) + self.lists_of_internal_token_boundaries_and_special_tokens(sentence)
                yield sentence_and_token_information
                if file_output:
                    lowered_text = sentence_and_token_information[0].lower()
                    lowered_sentence_and_token_information = (lowered_text, sentence_and_token_information[1], sentence_and_token_information[2])
                    self.unicode_outfile_obj.write(u' '.join(self.tokenised_text(lowered_sentence_and_token_information).split()) + u'\n')
        


if __name__ == '__main__':

    st = NLTKSegmenterPlusTokeniser(sys.stdin, sys.stdout)
    for sti in st.segmented_and_tokenised():
        pass
