# L. Amber Wilcox-O'Hearn 2013
# test_Constructor.py

import Constructor
import unittest, os, shutil, StringIO, random


class UtilityFunctionsTest(unittest.TestCase):

    def setUp(self):
        self.corpus_dir = 'test_data/'
        self.test_dir = 'tmp_test_dir/'
        os.mkdir(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_open_with_unicode(self):
        plaintext_file = self.corpus_dir + 'Wikipedia_smallest_subset'
        gzip_file = self.corpus_dir + 'Wikipedia_smaller_subset.gz'
        bzip2_file = self.corpus_dir + 'Wikipedia_small_subset.bz2'
        infile = Constructor.open_with_unicode(plaintext_file, None, 'r')
        outfile = Constructor.open_with_unicode(self.test_dir + 'test.gz', 'gzip', 'w')
        lines = infile.readlines()
        outfile.writelines(lines)
        infile = Constructor.open_with_unicode(gzip_file, 'gzip', 'r')
        outfile = Constructor.open_with_unicode(self.test_dir + 'test.bz2', 'bzip2', 'w')
        infile.readlines()
        outfile.writelines(lines)
        infile = Constructor.open_with_unicode(bzip2_file, 'bzip2', 'r')
        outfile = Constructor.open_with_unicode(self.test_dir + 'test.txt', None, 'w')
        infile.readlines()
        outfile.writelines(lines)

    def test_split_files_into_chunks(self):
        corpus_path = self.corpus_dir + 'Wikipedia_small_subset.bz2'
        Constructor.split_file_into_chunks(corpus_path, self.test_dir, 50)
        self.assertTrue(os.path.isdir(self.test_dir))
        for i in range(20):
            self.assertTrue(os.path.isfile(self.test_dir + '%03d' % i + '.bz2'))
        
        original_lines = Constructor.open_with_unicode(corpus_path, 'bzip2', 'r').readlines()
        first_chunk_lines = Constructor.open_with_unicode(self.test_dir + '000.bz2', 'bzip2', 'r').readlines()
        mid_chunk_lines = Constructor.open_with_unicode(self.test_dir + '009.bz2', 'bzip2', 'r').readlines()
        last_chunk_lines = Constructor.open_with_unicode(self.test_dir + '019.bz2', 'bzip2', 'r').readlines()
        
        self.assertEqual(original_lines[0], first_chunk_lines[0]) 
        self.assertEqual(original_lines[24], first_chunk_lines[24]) 
        self.assertEqual(original_lines[49], first_chunk_lines[49]) 

        self.assertEqual(original_lines[450], mid_chunk_lines[0]) 
        self.assertEqual(original_lines[474], mid_chunk_lines[24]) 
        self.assertEqual(original_lines[499], mid_chunk_lines[49]) 

        self.assertEqual(original_lines[950], last_chunk_lines[0]) 
        self.assertEqual(original_lines[974], last_chunk_lines[24]) 
        self.assertEqual(original_lines[993], last_chunk_lines[43]) 
        
class MockTargetOrSourceElement():
    def __init__(self, path_name):
        self.path = path_name

class BuilderFunctionsTest(unittest.TestCase):

    """
    These are regression tests, not unit tests.
    """

    def setUp(self):

        self.test_dir = 'tmp_test_dir/'
        os.mkdir(self.test_dir)
        corpus_path = "test_data/Wikipedia_small_subset.bz2"
        vocabulary_sizes = [.05, .1]
        error_rate = .1

        self.builder = Constructor.Constructor(corpus_path, vocabulary_sizes, self.test_dir, error_rate, self.test_dir)

#    def tearDown(self):
#        shutil.rmtree(self.test_dir)

    def test_randomize_wikipedia_articles(self):

        training_file_name = self.test_dir + 'training_file.bz2'
        devel_file_name = self.test_dir + 'devel_file.bz2'
        testing_file_name = self.test_dir + 'testing_file.bz2'

        article_file_name = MockTargetOrSourceElement(self.builder.corpus_path)
        train_file_name = MockTargetOrSourceElement(training_file_name)
        devel_file_name = MockTargetOrSourceElement(devel_file_name)
        test_file_name = MockTargetOrSourceElement(testing_file_name)
        self.builder.randomise_wikipedia_articles([train_file_name, devel_file_name, test_file_name], [article_file_name], None)

        training_lines = Constructor.open_with_unicode(training_file_name, 'bzip2', 'r').readlines()
        devel_lines = Constructor.open_with_unicode(devel_file_name, 'bzip2', 'r').readlines()
        testing_lines = Constructor.open_with_unicode(testing_file_name, 'bzip2', 'r').readlines()

        self.assertEqual(training_lines[0], u'Anarchism.\n')
        self.assertEqual(training_lines[163], u'Alabama.\n')
        self.assertEqual(training_lines[893], u'---END.OF.DOCUMENT---\n')
        self.assertEqual(devel_lines[0], u'Albedo.\n')
        self.assertEqual(devel_lines[46], u'Alain Connes.\n')
        self.assertEqual(devel_lines[54], u'---END.OF.DOCUMENT---\n')
        self.assertEqual(testing_lines[0], u'International Atomic Time.\n')
        self.assertEqual(testing_lines[15], u'Allan Dwan.\n')
        self.assertEqual(testing_lines[27], u'---END.OF.DOCUMENT---\n')

    def test_create_vocabularies(self):
        target = [MockTargetOrSourceElement(f) for f in [self.test_dir + str(size) + 'K.vocab' for size in self.builder.vocabulary_sizes]]
        source = [MockTargetOrSourceElement(self.builder.corpus_path)]

        self.builder.create_vocabularies(target, source, None)
        

    def test_create_trigram_models(self):
        self.fail()

    def test_extract_real_word_vocabulary(self):
        self.fail()

    def test_create_error_sets(self):
        self.fail()

if __name__ == '__main__':
    unittest.main()
