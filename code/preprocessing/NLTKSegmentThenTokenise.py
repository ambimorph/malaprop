# 2012 L. Amber Wilcox-O'Hearn
# NLTKSegmentThenTokenise.py

import nltk
import re, sys, codecs, unicodedata, string

# TODO: 
# Refactor to output either:
# 1: List of tuples, where the tuples correspond to the segmentation decisions of PunktSentenceTokenizer (+ hack): 
# first item: sentence with whitespace lossily collapsed into a single space,
# second item: list of token segmentation points, including at whitespace.
# 2: Plain text output of segmentation points applied to sentences, as well as lowercasing and number transforms, if desired.

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

        self._ellipses_and_whitespace_regexps = [
                (re.compile(r'(\.\.+)', re.U), r' \1 '),
                (re.compile(r'^(\s)+', re.U), r''),
                (re.compile(r'(\s)+$', re.U), r''),
                (re.compile(r'\n', re.U), r'<NEWLINE>'),
                (re.compile(r'(\s)+', re.U), r' '),
                (re.compile(r'(\s)*<NEWLINE>(\s)*', re.U), r'\n'),
            ]

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
                


    def split_sentence_final_period_when_not_abbreviation(self, segmenter, sent_text):
        i = len(sent_text) - 1
        while unicodedata.category(sent_text[i])[0] not in 'LN':
            i -= 1
            if i == -1:
                return sent_text
        if i == len(sent_text) - 1 or sent_text[i+1] != '.':
            return sent_text
        period_index = i+1
        # See if preceding token is an abbreviation.
        while unicodedata.category(sent_text[i]) != 'Zs' and i >= 0:
            i -= 1
        token_index = i+1
        abbreviations = segmenter._params.abbrev_types
        if sent_text[token_index:period_index].lower() not in abbreviations:
            return sent_text[0:period_index] + ' ' + sent_text[period_index:]
        return sent_text

    def space_separate_non_period_punctuation_and_regularize_digit_strings(self, line):
        # if any chars are unicode punctuation and not periods, pad them with space,
        # except at the beginning and end of the line, unless it is a
        # contraction or an inter-numeric comma.
        # replace strings of digits and commas with '<n-digit-integer>'
        # I've traded some readability for doing it in one pass.

        new_line = u''
        last_index = 0
        digit_length = 0
        number_punct = False
        if unicodedata.category(line[0]) == 'Nd':
            digit_length = 1
        elif unicodedata.category(line[0])[0] in 'PS' and line[0] != '.':
            new_line +=  line[0] + u' '
            last_index = 1
        for i in [x+1 for x in range(len(line)-1)]:
            if unicodedata.category(line[i]) == 'Nd':
                # We're in a digit string.
                if digit_length == 0:
                    new_line += line[last_index:i]
                last_index = i+1
                digit_length += 1
            else:
                if digit_length > 0:
                    # Either there is a period or comma in the digit string or
                    # this ends the digit string. 
                    if (line[i] == '.' or line[i] == ',') and i < len(line)-1 and unicodedata.category(line[i+1]) =='Nd':
                        number_punct = True
                    new_line += u'<' + unicode(str(digit_length)) + u'-digit-integer>'
                    digit_length = 0
                    last_index = i
                if unicodedata.category(line[i])[0] in 'PS' and line[i] != '.' and not number_punct:
                    if (line[i] == '\'' or line[i] == u'\xb4') and unicodedata.category(line[i-1])[0] == 'L' \
                        and i < len(line)-1 and unicodedata.category(line[i+1])[0] == 'L':
                        pass
                    else:
                        new_line += line[last_index:i] + u' ' + line[i] + u' '
                        last_index = i+1
                number_punct = False
        new_line  += line[last_index:]
        return new_line

    def clean_up_ellipses_and_whitespace_and_make_all_lowercase(self, line):

        line = line.lower()
        for (regexp, repl) in self._ellipses_and_whitespace_regexps:
            line = regexp.sub(repl, line)
        return line

    def segment_and_tokenise(self, text=None):
        assert text is None or isinstance(text, unicode), text

        if text == None: text = self.text
        for line in (t for t in text.split('\n')):
            sentences = self.sbd.sentences_from_text(line, realign_boundaries=True)
            sentences = self.apply_ugly_hack_to_reattach_wrong_splits_in_certain_cases_with_initials(sentences)
            for sentence in sentences:
                sentence = self.split_sentence_final_period_when_not_abbreviation(self.sbd, sentence)
                sentence = self.space_separate_non_period_punctuation_and_regularize_digit_strings(sentence)
                sentence = self.clean_up_ellipses_and_whitespace_and_make_all_lowercase(sentence)
                self.unicode_outfile_obj.write(sentence)
                self.unicode_outfile_obj.write('\n')


    def lists_of_internal_token_boundaries_and_special_tokens(self, line):
        # if any chars are unicode punctuation and not periods, pad them with space,
        # except at the beginning and end of the line, unless it is a
        # contraction or an inter-numeric comma.
        # replace strings of digits and commas with '<n-digit-integer>'
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

    def tokenise(self, sentence_and_token_information):
        return u''

    def segmented_and_tokenised(self, text=None, file_output=False):
        assert text is None or isinstance(text, unicode), text
        if text == None: text = self.text
        for line in (t for t in text.split('\n')):
            sentences = self.sbd.sentences_from_text(line, realign_boundaries=True)
            sentences = self.apply_ugly_hack_to_reattach_wrong_splits_in_certain_cases_with_initials(sentences)
            for sentence in sentences:
                sentence_and_token_information = (sentence,) + self.lists_of_internal_token_boundaries_and_special_tokens(sentence)
                yield sentence_and_token_information
                if file_output:
                    self.unicode_outfile_obj.write(self.tokenise(sentence_and_token_information)) # include \n here
        


if __name__ == '__main__':

    st = NLTKSegmenterPlusTokeniser(sys.stdin, sys.stdout)
    st.segment_and_tokenise()
