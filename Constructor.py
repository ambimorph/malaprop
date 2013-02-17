# L. Amber Wilcox-O'Hearn 2013
# Constructor.py

import codecs, bz2, gzip, random, subprocess, os

from code.preprocessing import WikipediaArticleRandomiser
from code.language_modelling import vocabulary_cutter
from code.error_insertion import RealWordVocabExtractor
from code.error_insertion import RealWordErrorChannel

def open_with_unicode(file_name, compression_type, mode):
    assert mode in ['r', 'w']
    if compression_type == None:
        if mode == 'r':
            return codecs.getreader('utf-8')(open(file_name, mode))
        elif mode == 'w':
            return codecs.getwriter('utf-8')(open(file_name, mode))
    elif compression_type == 'gzip':
        if mode == 'r':
            return codecs.getreader('utf-8')(gzip.GzipFile(file_name, mode))
        elif mode == 'w':
            return codecs.getwriter('utf-8')(gzip.GzipFile(file_name, mode))
    elif compression_type == 'bzip2':
        if mode == 'r':
            return codecs.getreader('utf-8')(bz2.BZ2File(file_name, mode))
        elif mode == 'w':
            return codecs.getwriter('utf-8')(bz2.BZ2File(file_name, mode))

def split_file_into_chunks(file_name, chunk_path, lines_per_chunk=100000):

    print lines_per_chunk
    if not os.path.isdir(chunk_path):
        os.mkdir(chunk_path)
    file_obj = open_with_unicode(file_name, 'bzip2', 'r')
    current_line_number = 0
    current_file_number = 0
    end_of_file = False
    while not end_of_file:
        current_filename = chunk_path + '%03d' % current_file_number + '.bz2'
        current_file_obj = open_with_unicode(current_filename, 'bzip2', 'w')
        current_file_obj.write(file_obj.readline())
        current_line_number += 1
        while current_line_number % lines_per_chunk > 0:
            current_line = file_obj.readline()
            end_of_file = current_line == ''
            current_file_obj.write(current_line)
            current_line_number += 1
        current_file_number += 1
    return
    
class Constructor():

    def __init__(self, corpus_path, vocabulary_sizes, language_model_dir, error_rate, error_set_dir):

        self.corpus_path = corpus_path
        self.vocabulary_sizes = vocabulary_sizes
        self.language_model_dir = language_model_dir
        self.error_rate = error_rate
        self.error_set_dir = error_set_dir

    def randomise_wikipedia_articles(self, target, source, env):
        """
        target is a list of files corresponding to the training,
        development, and test sets.  source is a single bzipped file of
        wikipedia articles.
        """
        article_file_obj = open_with_unicode(source[0].path, 'bzip2', 'r')
        train_file_obj = open_with_unicode(target[0].path, 'bzip2', 'w')
        devel_file_obj = open_with_unicode(target[1].path, 'bzip2', 'w')
        test_file_obj = open_with_unicode(target[2].path, 'bzip2', 'w')
        rand_obj = random.Random(7)
        ar = WikipediaArticleRandomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, rand_obj)
        ar.randomise()
        return None

    def create_vocabularies(self, target, source, env):
        """
        For each n in vocabulary_sizes, gets the unigram counts from the
        source files and puts the n most frequent words in the vocabulary
        file.
        """
    
        temporary_chunk_directory = self.language_model_dir + 'temp_chunk_dir/'
        split_file_into_chunks(source[0].path, temporary_chunk_directory)
        file_names_file_obj = open(temporary_chunk_directory + 'file_names', 'w')
        file_names_file_obj.writelines([s + '\n' for s in os.listdir(temporary_chunk_directory) if s != 'file_names'])
    
        # Run srilm make/merge-batch-counts
    
        temporary_counts_directory = self.language_model_dir + 'temp_counts_directory/'
        os.mkdir(temporary_counts_directory)
        srilm_make_batch_counts = subprocess.call(['make-batch-counts', temporary_chunk_directory + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory, '-write-order 1'])
        srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])
    
        # Make vocabularies
    
        for i in range(len(vocabulary_sizes)):
            unigram_counts_file_obj = open_with_unicode(temporary_counts_directory + 'merge-iter7-1.ngrams.gz', 'gzip', 'r')
            size = vocabulary_sizes[i]
            vocabulary_file_name = self.language_model_dir + str(size) + 'K.vocab'
            assert target[i].path == vocabulary_file_name, 'Target was: ' + target[i].path
            vocabulary_file_obj = open_with_unicode(vocabulary_file_name, None, 'w')
            cutter = vocabulary_cutter.VocabularyCutter(unigram_counts_file_obj, vocabulary_file_obj)
            cutter.cut_vocabulary(size*1000)
    
        return None
    
    def create_trigram_models(self, target, source, env):
        
        split_training_files_into_chunks(source[0].path)
    
        # Run srilm make/merge-batch-counts
    
        temporary_counts_directory = language_model_directory + 'temp_upto3_counts_directory/'
        if not os.path.isdir(temporary_counts_directory): # or if can't find temporary_counts_directory + 'merge-iter7-1.ngrams.gz'
                srilm_make_batch_counts = subprocess.call(['make-batch-counts', training_chunk_path + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory])
                srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])
        for i in range(len(vocabulary_sizes)):
            size = vocabulary_sizes[i]
            vocabulary_file_name = language_model_directory + str(size) + 'K.vocab'
            trigram_model_name = language_model_directory + 'trigram_model_' + str(size) + 'K.arpa'
            assert target[i].path == trigram_model_name, target[i].path
            srilm_make_big_lm = subprocess.call(['make-big-lm', '-debug', '2', '-kndiscount3', '-unk', '-read', temporary_counts_directory + 'merge-iter7-1.ngrams.gz', '-vocab', vocabulary_file_name, '-lm', trigram_model_name])
    
        return None
    
    def split_development_files_into_chunks(development_file_name):
        """
        We take the development set and split it into files of 100000
        lines each so that the nltk segmenter can make counts without
        choking.
        """
        lines_per_development_chunk = 100000
        if not os.path.isdir(development_chunk_path):
            development_file_obj = open_with_unicode_bzip2(development_file_name, 'r')
            os.mkdir(development_chunk_path)
            current_line_number = 0
            current_file_number = 0
            while current_file_number < num_development_chunks:
                current_filename = development_chunk_path + 'development_set_chunk_%03d' % current_file_number + '.bz2'
                current_file_obj = open_with_unicode_bzip2(current_filename, 'w')
                current_file_obj.write(development_file_obj.readline())
                current_line_number += 1
                while current_line_number % lines_per_development_chunk > 0:
                    current_file_obj.write(development_file_obj.readline())
                    current_line_number += 1
                current_file_number += 1
        return
    
    def extract_real_word_vocabulary(self, target, source, env):
    
        for i in range(len(vocabulary_sizes)):
            size = vocabulary_sizes[i]
            vocabulary_file_name = language_model_directory + str(size) + 'K.vocab'
            vocabulary_file_obj = open(vocabulary_file_name, 'r')
            real_word_vocabulary_file_name = language_model_directory + str(size) + 'K.real_word_vocab'
    
            assert target[i].path == real_word_vocabulary_file_name, 'Target was: ' + target[i].path
            real_word_vocabulary_file_obj = open(real_word_vocabulary_file_name, 'w')
            extractor = RealWordVocabExtractor.RealWordVocabExtractor(vocabulary_file_obj, real_word_vocabulary_file_obj)
            extractor.extract_real_words()
        return
    
    def create_error_sets(self, target, source, env):
    
        split_development_files_into_chunks(source[0].path)
    
        for development_file_name in os.listdir(development_chunk_path):
            for i in range(len(vocabulary_sizes)):
                size = vocabulary_sizes[i]
                vocabulary_file_name = language_model_directory + str(size) + 'K.real_word_vocab'
                error_set_file_name = error_set_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary' + '_' + development_file_name
                corrections_file_name = error_set_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary' + '_' + development_file_name
                rwec = RealWordErrorChannel.RealWordErrorChannel(bz2.BZ2File(development_chunk_path + development_file_name, 'r'), \
                          open(vocabulary_file_name, 'r'), bz2.BZ2File(error_set_file_name, 'w'), open(corrections_file_name, 'w'), \
                          error_rate, random.Random(7))
                rwec.pass_file_through_channel()
                print development_file_name, rwec.get_stats()
    
        return None
    
        
