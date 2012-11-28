# 2012 L. Amber Wilcox-O'Hearn
# test_NLTKSegmentThenTokenise.py

import NLTKSegmentThenTokenise, unittest, StringIO


class SegmenterAndTokeniserTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.training_text_file = open('test_data/segmenter_training', 'r')

    def run_assertions(self, tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output):
        
        list_output = [x for x in tuple_generator]

        try:
            assert len(list_output) == len(expected_list_of_tuple_output)
            for i in range(len(list_output)):
                assert list_output[i] == expected_list_of_tuple_output[i]
        except AssertionError, exp:
            print "Expected ", 
            for tup in expected_list_of_tuple_output:
                print tup,
            print "\nbut got ", 
            for tup in list_output:
                print tup
            raise exp

        assert isinstance(out_file_obj.getvalue(), str), (type(out_file_obj.getvalue()), repr(out_file_obj.getvalue()))
        try:
            assert out_file_obj.getvalue() == expected_text_output
        except AssertionError, exp:
            x = out_file_obj.getvalue()
            for i in range(len(x)):
                if i >= len(expected_text_output) or x[i] != expected_text_output[i]: break
            print 'Matching prefix of output and expected output: ', repr(x[:i])
            print '\noutput differs starting here: ', repr(x[i:])
            print '\nexpected: ', repr(expected_text_output[i:])
            raise exp

    def test_unicode(self):

        text_to_segment_tokenise = 'The term "anarchism" derives from the Greek \xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82, "anarchos", meaning "without rulers", from the prefix \xe1\xbc\x80\xce\xbd- ("an-", "without") + \xe1\xbc\x80\xcf\x81\xcf\x87\xce\xae ("arch\xc3\xaa", "sovereignty, realm, magistracy") + -\xce\xb9\xcf\x83\xce\xbc\xcf\x8c\xcf\x82 ("-ismos", from the suffix -\xce\xb9\xce\xb6\xce\xb5\xce\xb9\xce\xbd, "-izein" "-izing").\nHere\xc2\xa0are\xc2\xa0some\xc2\xa0\nNBSPs!'.decode('utf-8')
        expected_list_of_tuple_output = [\
           ('The term "anarchism" derives from the Greek \xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82, "anarchos", meaning "without rulers", from the prefix \xe1\xbc\x80\xce\xbd- ("an-", "without") + \xe1\xbc\x80\xcf\x81\xcf\x87\xce\xae ("arch\xc3\xaa", "sovereignty, realm, magistracy") + -\xce\xb9\xcf\x83\xce\xbc\xcf\x8c\xcf\x82 ("-ismos", from the suffix -\xce\xb9\xce\xb6\xce\xb5\xce\xb9\xce\xbd, "-izein" "-izing").'.decode('utf-8'), \
           [3, 4, 8, 9, 10, 19, 20, 21, 28, 29, 33, 34, 37, 38, 43, 44, 51, 52, 53, 54, 62, 63, 64, 65, 72, 73, 74, 81, 82, 88, 89, 90, 91, 95, 96, 99, 100, 106, 107, 109, 110, 111, 112, 113, 115, 116, 117, 118, 119, 120, 127, 128, 129, 130, 131, 132, 136, 137, 138, 139, 144, 145, 146, 147, 148, 159, 160, 161, 166, 167, 168, 178, 179, 180, 181, 182, 183, 184, 189, 190, 191, 192, 193, 198, 199, 200, 201, 205, 206, 209, 210, 216, 217, 218, 223, 224, 225, 226, 227, 232, 233, 234, 235, 236, 241, 242, 243], \
           []), \
           ('Here\xc2\xa0are\xc2\xa0some'.decode('utf-8'), [4, 5, 8, 9], []), \
           (u'NBSPs!', [5], [])]
        expected_text_output = 'the term " anarchism " derives from the greek \xe1\xbc\x84\xce\xbd\xce\xb1\xcf\x81\xcf\x87\xce\xbf\xcf\x82 , " anarchos " , meaning " without rulers " , from the prefix \xe1\xbc\x80\xce\xbd - ( " an - " , " without " ) + \xe1\xbc\x80\xcf\x81\xcf\x87\xce\xae ( " arch\xc3\xaa " , " sovereignty , realm , magistracy " ) + - \xce\xb9\xcf\x83\xce\xbc\xcf\x8c\xcf\x82 ( " - ismos " , from the suffix - \xce\xb9\xce\xb6\xce\xb5\xce\xb9\xce\xbd , " - izein " " - izing " ) .\nhere are some\nnbsps !\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        seg_tok.segment_and_tokenise(text_to_segment_tokenise)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_sentence_segmentation(self):

        text_to_segment_tokenise = u'Another libertarian tradition is that of unschooling and the free school in which child-led activity replaces pedagogic approaches. Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921. Summerhill is often cited as an example of anarchism in practice. However, although Summerhill and other free schools are radically libertarian, they differ in principle from those of Ferrer by not advocating an overtly-political class struggle-approach.\nThe Academy of Motion Picture Arts and Sciences itself was conceived by Metro-Goldwyn-Mayer studio boss Louis B. Mayer.  The 1st Academy Awards ceremony was held on Thursday, May 16, 1929, at the Hotel Roosevelt in Hollywood to honor outstanding film achievements of 1927 and 1928.\nWhen the Western Roman Empire collapsed, Berbers became independent again in many areas, while the Vandals took control over other parts, where they remained until expelled by the generals of the Byzantine Emperor, Justinian I. The Byzantine Empire then retained a precarious grip on the east of the country until the coming of the Arabs in the eighth century.'
        expected_list_of_tuple_output = [ \
            (u'Another libertarian tradition is that of unschooling and the free school in which child-led activity replaces pedagogic approaches.', \
            [7, 8, 19, 20, 29, 30, 32, 33, 37, 38, 40, 41, 52, 53, 56, 57, 60, 61, 65, 66, 72, 73, 75, 76, 81, 82, 91, 92, 100, 101, 109, 110, 119, 120, 130], \
            []), \
            (u'Experiments in Germany led to A. S. Neill founding what became Summerhill School in 1921.', \
            [11, 12, 14, 15, 22, 23, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 41, 42, 50, 51, 55, 56, 62, 63, 73, 74, 80, 81, 83, 84, 88], \
            [(84, 4, '<4-digit-integer>')]), \
            (u'Summerhill is often cited as an example of anarchism in practice.', \
            [10, 11, 13, 14, 19, 20, 25, 26, 28, 29, 31, 32, 39, 40, 42, 43, 52, 53, 55, 56, 64], \
            []), \
            (u'However, although Summerhill and other free schools are radically libertarian, they differ in principle from those of Ferrer by not advocating an overtly-political class struggle-approach.', \
            [7, 8, 9, 17, 18, 28, 29, 32, 33, 38, 39, 43, 44, 51, 52, 55, 56, 65, 66, 77, 78, 79, 83, 84, 90, 91, 93, 94, 103, 104, 108, 109, 114, 115, 117, 118, 124, 125, 127, 128, 131, 132, 142, 143, 145, 146, 153, 154, 163, 164, 169, 170, 178, 179, 187], \
            []), \
            (u'The Academy of Motion Picture Arts and Sciences itself was conceived by Metro-Goldwyn-Mayer studio boss Louis B. Mayer.', \
            [3, 4, 11, 12, 14, 15, 21, 22, 29, 30, 34, 35, 38, 39, 47, 48, 54, 55, 58, 59, 68, 69, 71, 72, 77, 78, 85, 86, 91, 92, 98, 99, 103, 104, 109, 110, 112, 113, 118], \
            []), \
            (u'The 1st Academy Awards ceremony was held on Thursday, May 16, 1929, at the Hotel Roosevelt in Hollywood to honor outstanding film achievements of 1927 and 1928.', \
            [3, 4, 7, 8, 15, 16, 22, 23, 31, 32, 35, 36, 40, 41, 43, 44, 52, 53, 54, 57, 58, 60, 61, 62, 66, 67, 68, 70, 71, 74, 75, 80, 81, 90, 91, 93, 94, 103, 104, 106, 107, 112, 113, 124, 125, 129, 130, 142, 143, 145, 146, 150, 151, 154, 155, 159], \
            [(4, 1, '<1-digit-integer>'), (58, 2, '<2-digit-integer>'), (62, 4, '<4-digit-integer>'), (146, 4, '<4-digit-integer>'), (155, 4, '<4-digit-integer>')]), \
            (u'When the Western Roman Empire collapsed, Berbers became independent again in many areas, while the Vandals took control over other parts, where they remained until expelled by the generals of the Byzantine Emperor, Justinian I.', \
            [4, 5, 8, 9, 16, 17, 22, 23, 29, 30, 39, 40, 41, 48, 49, 55, 56, 67, 68, 73, 74, 76, 77, 81, 82, 87, 88, 89, 94, 95, 98, 99, 106, 107, 111, 112, 119, 120, 124, 125, 130, 131, 136, 137, 138, 143, 144, 148, 149, 157, 158, 163, 164, 172, 173, 175, 176, 179, 180, 188, 189, 191, 192, 195, 196, 205, 206, 213, 214, 215, 224, 225], \
            []), \
            (u'The Byzantine Empire then retained a precarious grip on the east of the country until the coming of the Arabs in the eighth century.', \
            [3, 4, 13, 14, 20, 21, 25, 26, 34, 35, 36, 37, 47, 48, 52, 53, 55, 56, 59, 60, 64, 65, 67, 68, 71, 72, 79, 80, 85, 86, 89, 90, 96, 97, 99, 100, 103, 104, 109, 110, 112, 113, 116, 117, 123, 124, 131], \
            [])]
        expected_text_output = 'another libertarian tradition is that of unschooling and the free school in which child - led activity replaces pedagogic approaches .\nexperiments in germany led to a. s. neill founding what became summerhill school in <4-digit-integer> .\nsummerhill is often cited as an example of anarchism in practice .\nhowever , although summerhill and other free schools are radically libertarian , they differ in principle from those of ferrer by not advocating an overtly - political class struggle - approach .\nthe academy of motion picture arts and sciences itself was conceived by metro - goldwyn - mayer studio boss louis b. mayer .\nthe <1-digit-integer>st academy awards ceremony was held on thursday , may <2-digit-integer> , <4-digit-integer> , at the hotel roosevelt in hollywood to honor outstanding film achievements of <4-digit-integer> and <4-digit-integer> .\nwhen the western roman empire collapsed , berbers became independent again in many areas , while the vandals took control over other parts , where they remained until expelled by the generals of the byzantine emperor , justinian i .\nthe byzantine empire then retained a precarious grip on the east of the country until the coming of the arabs in the eighth century .\n'
            
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)


    def test_quotations_and_multiple_punctuation(self):

        text_to_segment_tokenise = u'Accordingly, "libertarian socialism" is sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism). On the other hand, some use "libertarianism" to refer to individualistic free-market philosophy only, referring to free-market anarchism as "libertarian anarchism." '+"Citizens can oppose a decision ('besluit') made by a public body ('bestuursorgaan') within the administration\nThe Treaty could be considered unpopular in Scotland: Sir George Lockhart of Carnwath, the only member of the Scottish negotiating team against union, noted that `The whole nation appears against the Union' and even Sir John Clerk of Penicuik, an ardent pro-unionist and Union negotiator, observed that the treaty was `contrary to the inclinations of at least three-fourths of the Kingdom'."
        expected_list_of_tuple_output = [ \
            (u'Accordingly, "libertarian socialism" is sometimes used as a synonym for socialist anarchism, to distinguish it from "individualist libertarianism" (individualist anarchism).', \
            [11, 12, 13, 14, 25, 26, 35, 36, 37, 39, 40, 49, 50, 54, 55, 57, 58, 59, 60, 67, 68, 71, 72, 81, 82, 91, 92, 93, 95, 96, 107, 108, 110, 111, 115, 116, 117, 130, 131, 145, 146, 147, 148, 161, 162, 171, 172], \
            []), \
            (u'On the other hand, some use "libertarianism" to refer to individualistic free-market philosophy only, referring to free-market anarchism as "libertarian anarchism."', \
            [2, 3, 6, 7, 12, 13, 17, 18, 19, 23, 24, 27, 28, 29, 43, 44, 45, 47, 48, 53, 54, 56, 57, 72, 73, 77, 78, 84, 85, 95, 96, 100, 101, 102, 111, 112, 114, 115, 119, 120, 126, 127, 136, 137, 139, 140, 141, 152, 153, 162, 163], \
            []), \
            (u"Citizens can oppose a decision ('besluit') made by a public body ('bestuursorgaan') within the administration", \
            [8, 9, 12, 13, 19, 20, 21, 22, 30, 31, 32, 33, 40, 41, 42, 43, 47, 48, 50, 51, 52, 53, 59, 60, 64, 65, 66, 67, 81, 82, 83, 84, 90, 91, 94, 95], \
            []), \
            (u"The Treaty could be considered unpopular in Scotland: Sir George Lockhart of Carnwath, the only member of the Scottish negotiating team against union, noted that `The whole nation appears against the Union' and even Sir John Clerk of Penicuik, an ardent pro-unionist and Union negotiator, observed that the treaty was `contrary to the inclinations of at least three-fourths of the Kingdom'.", \
            [3, 4, 10, 11, 16, 17, 19, 20, 30, 31, 40, 41, 43, 44, 53, 54, 57, 58, 64, 65, 73, 74, 76, 77, 85, 86, 87, 90, 91, 95, 96, 102, 103, 105, 106, 109, 110, 118, 119, 130, 131, 135, 136, 143, 144, 149, 150, 151, 156, 157, 161, 162, 163, 166, 167, 172, 173, 179, 180, 187, 188, 195, 196, 199, 200, 205, 206, 207, 210, 211, 215, 216, 219, 220, 224, 225, 230, 231, 233, 234, 242, 243, 244, 246, 247, 253, 254, 257, 258, 266, 267, 270, 271, 276, 277, 287, 288, 289, 297, 298, 302, 303, 306, 307, 313, 314, 317, 318, 319, 327, 328, 330, 331, 334, 335, 347, 348, 350, 351, 353, 354, 359, 360, 365, 366, 373, 374, 376, 377, 380, 381, 388, 389], \
            [])]
        expected_text_output = 'accordingly , " libertarian socialism " is sometimes used as a synonym for socialist anarchism , to distinguish it from " individualist libertarianism " ( individualist anarchism ) .\non the other hand , some use " libertarianism " to refer to individualistic free - market philosophy only , referring to free - market anarchism as " libertarian anarchism . "\n'+"citizens can oppose a decision ( ' besluit ' ) made by a public body ( ' bestuursorgaan ' ) within the administration\nthe treaty could be considered unpopular in scotland : sir george lockhart of carnwath , the only member of the scottish negotiating team against union , noted that ` the whole nation appears against the union ' and even sir john clerk of penicuik , an ardent pro - unionist and union negotiator , observed that the treaty was ` contrary to the inclinations of at least three - fourths of the kingdom ' .\n"
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_ints_with_or_without_following_punctuation(self):
        text_to_segment_tokenise = u'Hidehiko Shimizu (born 4 November 1954) is a former Japanese football player. He has played for Nissan Motors.'
        expected_list_of_tuple_output = [ \
            (u'Hidehiko Shimizu (born 4 November 1954) is a former Japanese football player.', \
            [8, 9, 16, 17, 18, 22, 23, 24, 25, 33, 34, 38, 39, 40, 42, 43, 44, 45, 51, 52, 60, 61, 69, 70, 76], \
            [(23, 1, '<1-digit-integer>'), (34, 4, '<4-digit-integer>')]), \
            (u'He has played for Nissan Motors.', \
            [2, 3, 6, 7, 13, 14, 17, 18, 24, 25, 31], \
            [])]
        expected_text_output = 'hidehiko shimizu ( born <1-digit-integer> november <4-digit-integer> ) is a former japanese football player .\nhe has played for nissan motors .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_end_of_document(self):
        text_to_segment_tokenise = u'---END.OF.DOCUMENT---'
        expected_list_of_tuple_output = [(u'---END.OF.DOCUMENT---', [1, 2, 3, 18, 19, 20], [])]
        expected_text_output = '- - - end.of.document - - -\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_elipses(self):
        text_to_segment_tokenise = u"Elipses here... and there..."
        expected_list_of_tuple_output = [(u"Elipses here... and there...", [7, 8, 12, 15, 16, 19, 20, 25], [])]
        expected_text_output = 'elipses here ... and there ...\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_single_quotes(self):
        text_to_segment_tokenise = u"this 'could' be"
        expected_list_of_tuple_output = [(u"this 'could' be", [4, 5, 6, 11, 12, 13], [])]
        expected_text_output = 'this \' could \' be\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_mid_word(self):
        text_to_segment_tokenise = u'a line-or-three or 100,000.1 lines.  This&that.\nH. Amber Wilcox-O\'Hearn\n'+"They're his, not my brother's.\n3m/s"
        expected_list_of_tuple_output = [ \
            ( u'a line-or-three or 100,000.1 lines.', \
            [1, 2, 6, 7, 9, 10, 15, 16, 18, 19, 28, 29, 34], \
            [(19, 9, '<3-digit-integer>,<3-digit-integer>.<1-digit-integer>')]), \
            (u'This&that.', [4, 5], []), \
            (u'H. Amber Wilcox-O\'Hearn', [2, 3, 8, 9, 15, 16], []), \
            (u"They're his, not my brother's", [7, 8, 11, 12, 13, 16, 17, 19, 20], []), \
            (u"3m/s", [2, 3], [(0, 2, '<1-digit-integer>m')])]
        expected_text_output = 'a line - or - three or <3-digit-integer>,<3-digit-integer>.<1-digit-integer> lines .\nthis & that .\nh. amber wilcox - o\'hearn\nthey\'re his , not my brother\'s .\n<1-digit-integer>m / s\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_sentence_final_punctuation(self):
        text_to_segment_tokenise = u'Finally.\nFinally?\nFinally!'
        expected_list_of_tuple_output = [ \
            (u'Finally.', [7], []),
            (u'Finally?', [7], []),
            (u'Finally!', [7], [])]
        expected_text_output = 'finally .\nfinally ?\nfinally !\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_dollar_percent_and_strings_of_consecutive_numbers(self):
        text_to_segment_tokenise = u"$1.50, 30%"
        expected_list_of_tuple_output = [(u"$1.50, 30%", [1, 5, 6, 7, 9], [(1, 4, '<1-digit-integer>.<2-digit-integer>'), (7, 2, '<2-digit-integer>')])]
        expected_text_output = '$ <1-digit-integer>.<2-digit-integer> , <2-digit-integer> %\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_line_starts_with_punct_or_number(self):
        text_to_segment_tokenise = u'"This 34.\n'
        expected_list_of_tuple_output = [(u'"This 34.', [1, 5, 6, 8], [(6, 2, '<2-digit-integer>')])]
        expected_text_output = '" this <2-digit-integer> .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_abbreviations(self):
        # This is, of course, incorrectly segmented, but correctly characterises the behaviour of the segmenter.
        text_to_segment_tokenise = u'Mr. Shimizu was not born in the U.S. "You are just joking."'
        expected_list_of_tuple_output = [ \
            (u'Mr. Shimizu was not born in the U.S. "You are just joking."', \
            [3, 4, 11, 12, 15, 16, 19, 20, 24, 25, 27, 28, 31, 32, 36, 37, 38, 41, 42, 45, 46, 50, 51, 57, 58], \
            [])]
        expected_text_output = 'mr. shimizu was not born in the u.s. " you are just joking . "\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_initials(self):
        text_to_segment_tokenise = u'Neither was J. S. Bach.'
        expected_list_of_tuple_output = [(u'Neither was J. S. Bach.', [7, 8, 11, 12, 14, 15, 17, 18, 22], [])]
        expected_text_output = 'neither was j. s. bach .\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)

    def test_multiple_spaces_space_at_beginning_of_line(self):
        text_to_segment_tokenise = u'Extra  spaces     here \n and here'
        expected_list_of_tuple_output = [(u'Extra spaces here and here', [5, 6, 12, 13, 17, 18, 21, 22], [])]
        expected_text_output = 'extra spaces here\nand here\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)
        
    def test_suffixes(self):
        text_to_segment_tokenise = u'Don\'t keep this together: -suffix'
        expected_list_of_tuple_output = [(u'Don\'t keep this together: -suffix', [5, 6, 10, 11, 15, 16, 24, 25, 26, 27], [])]
        expected_text_output = 'don\'t keep this together : - suffix\n'
        out_file_obj = StringIO.StringIO()
        seg_tok = NLTKSegmentThenTokenise.NLTKSegmenterPlusTokeniser(self.training_text_file, out_file_obj)
        tuple_generator = seg_tok.segmented_and_tokenised(text_to_segment_tokenise, file_output=True)
        self.run_assertions(tuple_generator, expected_list_of_tuple_output, out_file_obj, expected_text_output)


if __name__ == '__main__':
    unittest.main()
