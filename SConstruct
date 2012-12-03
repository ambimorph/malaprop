# L. Amber Wilcox-O'Hearn 2012
# SConstruct

import codecs, bz2, gzip, random, subprocess, os

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']

from code.preprocessing import WikipediaArticleRandomiser
from code.language_modelling import vocabulary_cutter
from code.error_insertion import RealWordErrorChannel

# Make these into one unicode open function with compression options.

def open_with_unicode_bzip2(file_name, mode):
    assert mode in ['r', 'w']
    if mode == 'r':
        return codecs.getreader('utf-8')(bz2.BZ2File(file_name, mode))
    elif mode == 'w':
        return codecs.getwriter('utf-8')(bz2.BZ2File(file_name, mode))

def open_with_unicode_gzip(file_name, mode):
    assert mode in ['r', 'w']
    if mode == 'r':
        return codecs.getreader('utf-8')(gzip.GzipFile(file_name, mode))
    elif mode == 'w':
        return codecs.getwriter('utf-8')(gzip.GzipFile(file_name, mode))

def open_with_unicode(file_name, mode):
    assert mode in ['r', 'w']
    if mode == 'r':
        return codecs.getreader('utf-8')(open(file_name, mode))
    elif mode == 'w':
        return codecs.getwriter('utf-8')(open(file_name, mode))

def randomise_wikipedia_articles(target, source, env):
    "target is a list of files corresponding to the training, development, and test sets.  source is a single bzipped file of wikipedia articles."
    article_file_obj = open_with_unicode_bzip2(source[0].path, 'r')
    train_file_obj = open_with_unicode_bzip2(target[0].path, 'w')
    devel_file_obj = open_with_unicode_bzip2(target[1].path, 'w')
    test_file_obj = open_with_unicode_bzip2(target[2].path, 'w')
    rand_obj = random.Random(7)
    ar = WikipediaArticleRandomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, rand_obj)
    ar.randomise()
# Somewhere, perhaps here, we ought to assert that the results give the following md5sums:
# 72c01f8951f8968788bea57034e121a0  training_set.bz2
# 19d502cfdedc5517e4b2a808171f9ac4  development_set.bz2
# e683df17e81a5732605eefc9618d0403  test_set.bz2
    return None

def split_training_files_into_chunks(training_file_name):

    # We take the training set and split it into files of 100000 lines each so that srilm can make counts without choking.
    # It also needs a list of the names of the resulting files.

    lines_per_chunk = 100000
    if not os.path.isdir(chunk_path):
        training_file_obj = open_with_unicode_bzip2(training_file_name, 'r')
        os.mkdir(chunk_path)
        file_names_file_obj = open(chunk_path + 'file_names', 'w')
        current_line_number = 0
        current_file_number = 0
        while current_file_number < num_chunks:
            current_filename = chunk_path + 'training_set_chunk_%03d' % current_file_number + '.bz2'
            file_names_file_obj.write(current_filename + '\n')
            current_file_obj = open_with_unicode_bzip2(current_filename, 'w')
            current_file_obj.write(training_file_obj.readline())
            current_line_number += 1
            while current_line_number % lines_per_chunk > 0:
                current_file_obj.write(training_file_obj.readline())
                current_line_number += 1
            current_file_number += 1

    return

def create_vocabularies(target, source, env):
    "For each n in vocabulary_sizes, gets the unigram counts from the source files and puts the n most frequent words in the vocabulary file."

    split_training_files_into_chunks(source[0].path)

    # Run srilm make/merge-batch-counts

    temporary_counts_directory = language_model_directory + 'temp_counts_directory/'
    if not os.path.isdir(temporary_counts_directory):
            srilm_make_batch_counts = subprocess.call(['make-batch-counts', chunk_path + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory, '-write-order 1'])
            srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])

    # Make vocabularies

    for i in range(len(vocabulary_sizes)):
        unigram_counts_file_obj = open_with_unicode_gzip(temporary_counts_directory + 'merge-iter7-1.ngrams.gz', 'r')
        size = vocabulary_sizes[i]
        vocabulary_file_name = language_model_directory + str(size) + 'K.vocab'
        assert target[i].path == vocabulary_file_name, 'Target was: ' + target[i].path
        vocabulary_file_obj = open_with_unicode(vocabulary_file_name, 'w')
        cutter = vocabulary_cutter.VocabularyCutter(unigram_counts_file_obj, vocabulary_file_obj)
        print "hello3"
        cutter.cut_vocabulary(size*1000)
        print "hello4"

    # Delete count files
    # shutil.rmtree(temporary_counts_directory)

    return None

def create_trigram_models(target, source, env):
    
    split_training_files_into_chunks(source[0].path)

    # Run srilm make/merge-batch-counts

    temporary_counts_directory = language_model_directory + 'temp_upto3_counts_directory/'
    if not os.path.isdir(temporary_counts_directory): # or if can't find temporary_counts_directory + 'merge-iter7-1.ngrams.gz'
            srilm_make_batch_counts = subprocess.call(['make-batch-counts', chunk_path + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory])
            srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])
    for i in range(len(vocabulary_sizes)):
        size = vocabulary_sizes[i]
        vocabulary_file_name = language_model_directory + str(size) + 'K.vocab'
        trigram_model_name = language_model_directory + 'trigram_model_' + str(size) + 'K.arpa'
        assert target[i].path == trigram_model_name, target[i].path
        srilm_make_big_lm = subprocess.call(['make-big-lm', '-debug', '2', '-kndiscount3', '-unk', '-read', temporary_counts_directory + 'merge-iter7-1.ngrams.gz', '-vocab', vocabulary_file_name, '-lm', trigram_model_name])

    # Do these only when everything else has worked!
    # shutil.rmtree(chunk_path)  
    # shutil.rmtree(temporary_counts_directory)

    return None

def split_development_files_into_chunks(development_file_name):

    # We take the development set and split it into files of 100000 lines each so that the nltk segmenter can make counts without choking.

    lines_per_chunk = 100000
    if not os.path.isdir(development_chunk_path):
        development_file_obj = open_with_unicode_bzip2(development_file_name, 'r')
        os.mkdir(development_chunk_path)
        current_line_number = 0
        current_file_number = 0
        while current_file_number < num_chunks:
            current_filename = development_chunk_path + 'development_set_chunk_%03d' % current_file_number + '.bz2'
            current_file_obj = open_with_unicode_bzip2(current_filename, 'w')
            current_file_obj.write(development_file_obj.readline())
            current_line_number += 1
            while current_line_number % lines_per_chunk > 0:
                current_file_obj.write(development_file_obj.readline())
                current_line_number += 1
            current_file_number += 1

    return
def create_error_sets(target, source, env):

    split_development_files_into_chunks(source[0].path)

    for development_file_name in os.listdir(development_chunk_path):
        for i in range(len(vocabulary_sizes)):
            size = vocabulary_sizes[i]
            vocabulary_file_name = language_model_directory + str(size) + 'K.vocab'
            rwec = RealWordErrorChannel.RealWordErrorChannel(bz2.BZ2File(development_chunk_path + development_file_name, 'r'), open(vocabulary_file_name, 'r'), bz2.BZ2File(target[i].path, 'w'), error_rate, random.Random(7))
            rwec.pass_file_through_channel()
            print rwec.get_stats()

    return None

data_directory = 'data/'
corpus_directory = data_directory + 'corpora/WestburyLab.wikicorp.201004/'
chunk_path = corpus_directory + 'training_set_chunks/'
development_chunk_path = corpus_directory + 'development_set_chunks/'
language_model_directory = data_directory + 'language_models/WestburyLab.wikicorp.201004/'
error_set_directory = data_directory + 'error_sets/WestburyLab.wikicorp.201004/'
num_chunks = 167
vocabulary_sizes = [50, 100]
error_rate = .05

learning_sets_builder = Builder(action = randomise_wikipedia_articles)
vocabulary_files_builder = Builder(action = create_vocabularies)
trigram_models_builder = Builder(action = create_trigram_models)
error_set_builder = Builder(action = create_error_sets)

env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'vocabulary_files' : vocabulary_files_builder, 'trigram_models' : trigram_models_builder, 'error_sets' : error_set_builder})

env.learning_sets([corpus_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], corpus_directory + 'WestburyLab.wikicorp.201004.txt.bz2')

env.vocabulary_files([language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes], [corpus_directory + 'training_set.bz2'])

env.trigram_models([language_model_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes], [corpus_directory + 'training_set.bz2'] + [language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.error_sets([error_set_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes], [corpus_directory + 'development_set.bz2'] + [language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])
