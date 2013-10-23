# real_word_error_inserter.py

import codecs, StringIO, json
from recluse.nltk_based_segmenter_tokeniser import *

class RealWordErrorInserter():

    def __init__(self, segmenter_tokeniser, vocabulary, error_channel):

        self.segmenter_tokeniser = segmenter_tokeniser
        self.vocabulary = vocabulary
        self.error_channel = error_channel

    def pass_sentence_through_channel(self, sentence):

        """
        Takes a string, tokenises, and passes each subtoken through
        the channel.  If any are changed, the token and subtoken
        indices are returned with the diff.
        """

        corrections = []
        token_list = list_subtokenise_and_regularise(sentence.split(), self.segmenter_tokeniser.sbd._params.abbrev_types)
        
        for t in range(len(token_list)):
            
            token = token_list[t]
            for s in range(len(token)):
                subtoken = token[s]
                if subtoken in self.vocabulary:
                    new_subtoken = StringIO.StringIO()
                    self.error_channel.write = new_subtoken.write
                    self.error_channel.accept_string(subtoken.lower())
                    if new_subtoken.getvalue() in self.vocabulary:
                        if new_subtoken.getvalue() != subtoken.lower():
                            if subtoken.islower():
                                replacement = new_subtoken.getvalue()
                            elif subtoken.istitle():
                                replacement = new_subtoken.getvalue().title()
                            else:
                                replacement = new_subtoken.getvalue().upper()
                            corrections.append([t, s, replacement, subtoken])

        if corrections == []: return None

        for correction in corrections:
            (t, s, replacement, subtoken) = correction
            token_list[t][s] = replacement

        return u' '.join([u''.join(subtoken) for subtoken in token_list]) + '\n', corrections


    def corrupt(self, text, file_dict, correction_task=False, adversarial_task=False, sentence_id=0):

        """
        The correction_task requires file objects in the dict for
        'corrupted' and 'corrections'; the adversarial_task
        'adversarial', and 'key'.
        """

        assert correction_task or adversarial_task
        if correction_task:
            corrupted_file_unicode_writer = codecs.getwriter('utf-8')(file_dict['corrupted'])
            corrections_file_unicode_writer = codecs.getwriter('utf-8')(file_dict['corrections'])
        if adversarial_task:
            adversarial_file_unicode_writer = codecs.getwriter('utf-8')(file_dict['adversarial'])
            key_file_unicode_writer = codecs.getwriter('utf-8')(file_dict['key'])

        first_sentence_id = sentence_id
        for sentence in self.segmenter_tokeniser.sentence_segment(text, tokenise=False, lower=False):

            corruption_and_corrections = self.pass_sentence_through_channel(sentence)
            if corruption_and_corrections is None:
                if correction_task:
                    corrupted_file_unicode_writer.write(sentence)
            else:
                corruption, corrections = corruption_and_corrections
                if correction_task:
                    corrupted_file_unicode_writer.write(corruption)
                    corrections_file_unicode_writer.write(json.dumps([sentence_id,  corrections]) + '\n')
                if adversarial_task:
                    alternatives = [sentence, corruption]
                    alternatives.sort()
                    adversarial_file_unicode_writer.write(json.dumps(alternatives) + '\n')
                    key_file_unicode_writer.write(unicode(int(alternatives[1] == sentence)))
            sentence_id += 1

        return sentence_id - first_sentence_id
            
