# 2012 L. Amber Wilcox-O'Hearn
# test_NLTKSegmentThenTokenise.py

import NLTKSegmentThenTokenise, unittest, StringIO


class SegmenterAndTokeniserTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.training_text_file = open('data/segmenter_training', 'r')

    def run_assertions(self, out_file_obj, expected_output):
    
        assert isinstance(out_file_obj.getvalue(), str), (type(out_file_obj.getvalue()), repr(out_file_obj.getvalue()))
        try:
            assert out_file_obj.getvalue() == expected_output
        except AssertionError, exp:
            x = out_file_obj.getvalue()
            for i in range(len(x)):
                if i >= len(expected_output) or x[i] != expected_output[i]: break
            print 'Matching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_output[i:])
            raise exp

    def test_unicode(self):

        text_to_segment_tokenise = 'The term "anarchism" derives from the Greek \xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82, "anarchos", meaning "without rulers", from the prefix \xe1\xbc\x80\xce\xbd- ("an-", "without") + \xe1\xbc\x80\xcf\x81\xcf\x87\xce\xae ("arch\xc3\xaa", "sovereignty, realm, magistracy") + -\xce\xb9\xcf\x83\xce\xbc\xcf\x8c\xcf\x82 ("-ismos", from the suffix -\xce\xb9\xce\xb6\xce\xb5\xce\xb9\xce\xbd, "-izein" "-izing").\nHere\xc2\xa0are\xc2\xa0some\xc2\xa0\nNBSPs!'.decode('utf-8')
        expected_output = 'the term " anarchism " derives from the greek \xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82 , " anarchos " , meaning " without rulers " , from the prefix \xe1\xbc\x80\xce\xbd - ( " an - " , " without " ) + \xe1\xbc\x80\xcf\x81\xcf\x87\xce\xae ( " arch\xc3\xaa " , " sovereignty , realm , magistracy " ) + - \xce\xb9\xcf\x83\xce\xbc\xcf\x8c\xcf\x82 ( " - ismos " , from the suffix - \xce\xb9\xce\xb6\xce\xb5\xce\xb9\xce\xbd , " - izein " " - izing " ) .\nhere are some\nnbsps !\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_sentence_segmentation(self):

        text_to_segment_tokenise = u'Another libertarian tradition is that of unschooling and the free school in which child-led activity replaces pedagogic approaches. Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921. Summerhill is often cited as an example of anarchism in practice. However, although Summerhill and other free schools are radically libertarian, they differ in principle from those of Ferrer by not advocating an overtly-political class struggle-approach.\nThe Academy of Motion Picture Arts and Sciences itself was conceived by Metro-Goldwyn-Mayer studio boss Louis B. Mayer.  The 1st Academy Awards ceremony was held on Thursday, May 16, 1929, at the Hotel Roosevelt in Hollywood to honor outstanding film achievements of 1927 and 1928.\nWhen the Western Roman Empire collapsed, Berbers became independent again in many areas, while the Vandals took control over other parts, where they remained until expelled by the generals of the Byzantine Emperor, Justinian I. The Byzantine Empire then retained a precarious grip on the east of the country until the coming of the Arabs in the eighth century.'
        expected_output = 'another libertarian tradition is that of unschooling and the free school in which child - led activity replaces pedagogic approaches .\nexperiments in germany led to a. s. neill founding what became summerhill school in <4-digit-integer> .\nsummerhill is often cited as an example of anarchism in practice .\nhowever , although summerhill and other free schools are radically libertarian , they differ in principle from those of ferrer by not advocating an overtly - political class struggle - approach .\nthe academy of motion picture arts and sciences itself was conceived by metro - goldwyn - mayer studio boss louis b. mayer .\nthe <1-digit-integer>st academy awards ceremony was held on thursday , may <2-digit-integer> , <4-digit-integer> , at the hotel roosevelt in hollywood to honor outstanding film achievements of <4-digit-integer> and <4-digit-integer> .\nwhen the western roman empire collapsed , berbers became independent again in many areas , while the vandals took control over other parts , where they remained until expelled by the generals of the byzantine emperor , justinian i .\nthe byzantine empire then retained a precarious grip on the east of the country until the coming of the arabs in the eighth century .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)


    def test_quotations_and_multiple_punctuation(self):

        text_to_segment_tokenise = u'Accordingly, "libertarian socialism" is sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism). On the other hand, some use "libertarianism" to refer to individualistic free-market philosophy only, referring to free-market anarchism as "libertarian anarchism." '+"Citizens can oppose a decision ('besluit') made by a public body ('bestuursorgaan') within the administration\nThe Treaty could be considered unpopular in Scotland: Sir George Lockhart of Carnwath, the only member of the Scottish negotiating team against union, noted that `The whole nation appears against the Union' and even Sir John Clerk of Penicuik, an ardent pro-unionist and Union negotiator, observed that the treaty was `contrary to the inclinations of at least three-fourths of the Kingdom'."
        expected_output = 'accordingly , " libertarian socialism " is sometimes used as a synonym for socialist anarchism , to distinguish it from " individualist libertarianism " ( individualist anarchism ) .\non the other hand , some use " libertarianism " to refer to individualistic free - market philosophy only , referring to free - market anarchism as " libertarian anarchism . "\n'+"citizens can oppose a decision ( ' besluit ' ) made by a public body ( ' bestuursorgaan ' ) within the administration\nthe treaty could be considered unpopular in scotland : sir george lockhart of carnwath , the only member of the scottish negotiating team against union , noted that ` the whole nation appears against the union ' and even sir john clerk of penicuik , an ardent pro - unionist and union negotiator , observed that the treaty was ` contrary to the inclinations of at least three - fourths of the kingdom ' .\n"
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_ints_with_or_without_following_punctuation(self):
        text_to_segment_tokenise = u'Hidehiko Shimizu (born 4 November 1954) is a former Japanese football player. He has played for Nissan Motors.'
        expected_output = 'hidehiko shimizu ( born <1-digit-integer> november <4-digit-integer> ) is a former japanese football player .\nhe has played for nissan motors .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_end_of_document(self):
        text_to_segment_tokenise = u'---END.OF.DOCUMENT---'
        expected_output = '- - - end.of.document - - -\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_elipses(self):
        text_to_segment_tokenise = u"Elipses here... and there..."
        expected_output = 'elipses here ... and there ...\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_single_quotes(self):
        text_to_segment_tokenise = u"this 'could' be"
        expected_output = 'this \' could \' be\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_mid_word(self):
        text_to_segment_tokenise = u'a line-or-three or 100,000.1 lines.  This&that.\nL. Amber Wilcox-O\'Hearn\n'+"They're his, not my brother's.\n3m/s"
        expected_output = 'a line - or - three or <3-digit-integer>,<3-digit-integer>.<1-digit-integer> lines .\nthis & that .\nl. amber wilcox - o\'hearn\nthey\'re his , not my brother\'s .\n<1-digit-integer>m / s\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_sentence_final_punctuation(self):
        text_to_segment_tokenise = u'Finally.\nFinally?\nFinally!'
        expected_output = 'finally .\nfinally ?\nfinally !\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_dollar_percent_and_strings_of_consecutive_numbers(self):
        text_to_segment_tokenise = u"$1.50, 30%"
        expected_output = '$ <1-digit-integer>.<2-digit-integer> , <2-digit-integer> %\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_line_starts_with_punct_or_number(self):
        text_to_segment_tokenise = u'"This 34.\n'
        expected_output = '" this <2-digit-integer> .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_abbreviations(self):
        text_to_segment_tokenise = u'Mr. Shimizu was not born in the U.S. "You are just an ignorant twit."'
        expected_output = 'mr. shimizu was not born in the u.s. " you are just an ignorant twit . "\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_initials(self):
        text_to_segment_tokenise = u'Neither was J. S. Bach.'
        expected_output = 'neither was j. s. bach .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)

    def test_multiple_spaces_space_at_beginning_of_line(self):
        text_to_segment_tokenise = u'Extra  spaces     here \n and here'
        expected_output = 'extra spaces here\nand here\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)
        

    def test_suffixes(self):
        text_to_segment_tokenise = u'Don\'t keep this together: -suffix'
        expected_output = 'don\'t keep this together : - suffix\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        self.run_assertions(out_file_obj, expected_output)


if __name__ == '__main__':
    unittest.main()
