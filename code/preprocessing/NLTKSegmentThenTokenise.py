# 2012 L. Amber Wilcox-O'Hearn
# NLTKSegmentThenTokenise.py

import nltk
import re, sys, codecs, unicodedata, string

# TODO: 
# Compensate for initials problem.
# Refactor to first create a nested list:
# Level 1: Split into sentences based on PunktSentenceTokenizer
# Level 2: Split on whitespace.  This is *lossy*, but that's what I intend right now.
# Level 3: This is where the segmenter comes in.  It will be a pair: the first is the string that actually appeared, the second is a list of segmented tokens.  This will deal with situations like punctuation to be separated from words, and classifiers like <4-digit-number>.
# Then there will be two ways to get the output: either return the list, or print the lossy segmented version. (?)

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
#        # Adding all letters as "abbreviations", since they are likely to occur as initials, even when not in the training data.
#        for l in unicode(string.ascii_letters):
#                self.sbd._params.abbrev_types.add(l)

        self._ellipses_and_whitespace_regexps = [
                (re.compile(r'(\.\.+)', re.U), r' \1 '),
                (re.compile(r'^(\s)+', re.U), r''),
                (re.compile(r'(\s)+$', re.U), r''),
                (re.compile(r'\n', re.U), r'<NEWLINE>'),
                (re.compile(r'(\s)+', re.U), r' '),
                (re.compile(r'(\s)*<NEWLINE>(\s)*', re.U), r'\n'),
            ]

    def reattach_wrong_splits_due_to_multiple_initials(self, lines):
        # NLTK currently splits sentences between 2 initials.  Hacking those back together.
        # Also has the effect of collapsing whitespace to a single space char.
        lines = list(lines)
        if len(lines) == 0: return []
        reattached_lines = []
        i = 0
        current_line = lines[i].split()
        while i < len(lines) - 1:
            next_line = lines[i+1].split()
            last_word = current_line[-1]
            current_line_ends_in_an_initial = False
            next_line_starts_with_an_initial = False
            if len(last_word) > 1 and (len(last_word) == 2 or unicodedata.category(last_word[-3]) in 'Zs'):
                if unicodedata.category(last_word[-2])[0] == 'L' and last_word[-1] == u'.':
                    current_line_ends_in_an_initial = True
                    first_word_of_next_line = next_line[0]
                    if len(first_word_of_next_line) > 1 and unicodedata.category(first_word_of_next_line[0])[0] == 'L' and first_word_of_next_line[1] == u'.':
                        if len(first_word_of_next_line) == 2 or unicodedata.category(first_word_of_next_line[2]) in 'Zs':
                                next_line_starts_with_an_initial = True
            if current_line_ends_in_an_initial and next_line_starts_with_an_initial:
                current_line += next_line
            else:
                reattached_lines.append(u' '.join(current_line))
                current_line = next_line
            i += 1 
        reattached_lines.append(u' '.join(current_line))
        return reattached_lines

    def is_an_initial(self, word):
        if len(word) == 2 and unicodedata.category(word[0])[0] == 'L' and word[1] == u'.':
            return True
        return False
    def starts_with_a_capital(self, word):
        if len(word) > 0 and unicodedata.category(word[0]) == 'Lu':
            return True
        return False
        

# do we need to insert extra breaks to solve justinian i. the?
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
            if self.is_an_initial(last_word):# and next_line_starts_with_a_capital:
                if unicodedata.category(first_word_of_next_line[0])[0] != 'L':
                    reattach = True
                elif next_line_starts_with_a_capital:
                    nltk_ortho_context = self.sbd._params.ortho_context[next_line[0].lower()]
                    if nltk_ortho_context <= 46:
                        reattach = True
                    else:
                        nltk_ortho_context_bit_string = bin(nltk_ortho_context)
                        if (len(nltk_ortho_context_bit_string) < 6 or nltk_ortho_context_bit_string[-4] == '0') and \
                                (len(nltk_ortho_context_bit_string) > 2 and nltk_ortho_context_bit_string[-1] == '1') or \
                                (len(nltk_ortho_context_bit_string) > 3 and nltk_ortho_context_bit_string[-2] == '1') or \
                                (len(nltk_ortho_context_bit_string) > 4 and nltk_ortho_context_bit_string[-3] == '1'):
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
    #        sentences = self.reattach_wrong_splits_due_to_multiple_initials(sentences)
            sentences = self.apply_ugly_hack_to_reattach_wrong_splits_in_certain_cases_with_initials(sentences)
            for sentence in sentences:
                sentence = self.split_sentence_final_period_when_not_abbreviation(self.sbd, sentence)
                sentence = self.space_separate_non_period_punctuation_and_regularize_digit_strings(sentence)
                sentence = self.clean_up_ellipses_and_whitespace_and_make_all_lowercase(sentence)
                self.unicode_outfile_obj.write(sentence)
                self.unicode_outfile_obj.write('\n')


if __name__ == '__main__':

    st = NLTKSegmenterPlusTokeniser(sys.stdin, sys.stdout)
    st.segment_and_tokenise()
