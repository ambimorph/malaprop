# L. Amber Wilcox-O'Hearn 2012
# SConstruct

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']

import codecs, bz2, gzip, random, subprocess, os, StringIO, filecmp

from code.preprocessing import WikipediaArticleRandomiser
from code.language_modelling import vocabulary_cutter
from code.error_insertion import RealWordVocabExtractor
from code.preprocessing import NLTKBasedSegmenterTokeniser
from code.error_insertion import RealWordErrorChannel

def open_with_unicode(file_name, compression_type, mode):
    assert compression_type in [None, 'gzip', 'bzip2']
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

def split_file_into_chunks(file_name, chunk_path):

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


def randomise_wikipedia_articles(target, source, env):
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


def create_vocabularies(target, source, env):
    """
    For each n in vocabulary_sizes, gets the unigram counts from the
    source files and puts the n most frequent words in the vocabulary
    file.
    """

    # Run srilm make/merge-batch-counts

    temporary_chunk_directory = data_directory + 'TEMP_CHUNK_DIR/'
    split_file_into_chunks(source[0].path, temporary_chunk_directory)
    file_names_file_obj = open(temporary_chunk_directory + 'file_names', 'w')
    file_names_file_obj.writelines([temporary_chunk_directory + s + '\n' for s in os.listdir(temporary_chunk_directory) if s != 'file_names'])
    file_names_file_obj.close()
    temporary_counts_directory = data_directory + 'TEMP_COUNTS_DIR/'
    srilm_make_batch_counts = subprocess.call(['make-batch-counts', temporary_chunk_directory + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory, '-write-order 1'])
    srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])

    # Make vocabularies

    for i in range(len(vocabulary_sizes)):
        merged_counts_file = [f for f in os.listdir(temporary_counts_directory) if f.endswith('.ngrams.gz')][0]
        unigram_counts_file_obj = open_with_unicode(temporary_counts_directory + merged_counts_file, 'gzip', 'r')
        size = vocabulary_sizes[i]
        vocabulary_file_name = data_directory + str(size) + 'K.vocab'
        assert target[i].path == vocabulary_file_name, 'Target was: ' + target[i].path + '; Expected: ' + vocabulary_file_name
        vocabulary_file_obj = open_with_unicode(vocabulary_file_name, None, 'w')
        cutter = vocabulary_cutter.VocabularyCutter(unigram_counts_file_obj, vocabulary_file_obj)
        cutter.cut_vocabulary(int(float(size)*1000))

    return None

def create_trigram_models(target, source, env):
    
    # Run srilm make/merge-batch-counts

    temporary_counts_directory = data_directory + 'TEMP_UPTO3_COUNTS_DIR/'
    temporary_chunk_directory = data_directory + 'TEMP_CHUNK_DIR/'
    if not os.path.isdir(temporary_chunk_directory):
        split_file_into_chunks(source[0].path, temporary_chunk_directory)
    srilm_make_batch_counts = subprocess.call(['make-batch-counts', temporary_chunk_directory + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', temporary_counts_directory])
    srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', temporary_counts_directory])
    for i in range(len(vocabulary_sizes)):
        size = vocabulary_sizes[i]
        vocabulary_file_name = data_directory + str(size) + 'K.vocab'
        merged_counts_file = [f for f in os.listdir(temporary_counts_directory) if f.endswith('.ngrams.gz')][0]
        trigram_model_name = data_directory + 'trigram_model_' + str(size) + 'K.arpa'
        assert target[i].path == trigram_model_name, target[i].path
        srilm_make_big_lm = subprocess.call(['make-big-lm', '-debug', '2', '-kndiscount3', '-unk', '-read', temporary_counts_directory + merged_counts_file, '-vocab', vocabulary_file_name, '-lm', trigram_model_name])

    return None

def extract_real_word_vocabulary(target, source, env):

    for i in range(len(vocabulary_sizes)):
        size = vocabulary_sizes[i]
        vocabulary_file_name = data_directory + str(size) + 'K.vocab'
        vocabulary_file_obj = open(vocabulary_file_name, 'r')
        real_word_vocabulary_file_name = data_directory + str(size) + 'K.real_word_vocab'

        assert target[i].path == real_word_vocabulary_file_name, 'Target was: ' + target[i].path
        real_word_vocabulary_file_obj = open(real_word_vocabulary_file_name, 'w')
        extractor = RealWordVocabExtractor.RealWordVocabExtractor(vocabulary_file_obj, real_word_vocabulary_file_obj)
        extractor.extract_real_words()
    return

def create_error_sets(target, source, env):

    for i in range(len(vocabulary_sizes)):
        size = vocabulary_sizes[i]
        vocabulary_file_name = data_directory + str(size) + 'K.real_word_vocab'
        error_set_file_name = data_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2'
        corrections_file_name = data_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2'
        rwec = RealWordErrorChannel.RealWordErrorChannel(open(vocabulary_file_name, 'r'), bz2.BZ2File(error_set_file_name, 'w'), bz2.BZ2File(corrections_file_name, 'w'), error_rate, random.Random(7))
        sentence_number = 0
        development_file_obj = bz2.BZ2File(source[0].path, 'r')
        line_number = 0
        line = development_file_obj.readline()
        while line:
            chunk = StringIO.StringIO(line)
            chunk.write(line)
            while line and line_number < lines_per_chunk:
                line = development_file_obj.readline()
                chunk.write(line)
                line_number += 1
            line_number = 0
            chunk.seek(0)
            segmenter_tokeniser = NLTKBasedSegmenterTokeniser.NLTKBasedSegmenterTokeniser(chunk)
            for sentence_obj in segmenter_tokeniser.segmented_and_tokenised():
            
                possibly_erroneous_sentence, corrections = rwec.pass_sentence_through_channel(sentence_obj)
                rwec.unicode_error_file_obj.write(possibly_erroneous_sentence + u'\n')
                if corrections != []:
                    rwec.unicode_corrections_file_obj.write(str(sentence_number) + ' ' + repr(corrections) + '\n')
                sentence_number += 1
        rwec.unicode_corrections_file_obj.write(rwec.get_stats())
        rwec.unicode_error_file_obj.close()
        rwec.unicode_corrections_file_obj.close()

    if TEST:
        assert filecmp.cmp(data_directory + 'errors_at_0.2_0.05K_vocabulary.bz2', 'test_data/errors_at_0.2_0.05K_vocabulary.bz2', shallow=False), "Test result errors_at_0.2_0.05K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'errors_at_0.2_0.5K_vocabulary.bz2', 'test_data/errors_at_0.2_0.5K_vocabulary.bz2', shallow=False), "Test result errors_at_0.2_0.5K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'corrections_0.2_0.05K_vocabulary.bz2', 'test_data/corrections_0.2_0.05K_vocabulary.bz2', shallow=False), "Test result corrections_0.2_0.05K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'corrections_0.2_0.5K_vocabulary.bz2', 'test_data/corrections_0.2_0.5K_vocabulary.bz2', shallow=False), "Test result corrections_0.2_0.5K_vocabulary.bz2 differs from expected."
        

    return None


# Get commandline configuration:

data_directory = ''
vocabulary_sizes = []
lines_per_chunk = 100000
error_rate = .05
TEST = False

try:
    data_directory = [x[1] for x in ARGLIST if x[0] == "data_directory"][0] + '/'
except:
    print "Usage: scons data_directory=DIR variables target"
    raise Exception

if [x for x in ARGLIST if x[0] == "test"]:
    TEST = True
    vocabulary_sizes = [0.05, 0.5]
    lines_per_chunk = 25
    error_rate = .2

elif [x for x in ARGLIST if x[0] == "replicate"]:
    vocabulary_sizes = [50, 100]
    lines_per_chunk = 100000
    error_rate = .05

else:
    for key, value in ARGLIST:
        if key == "vocabulary_size":
            vocabulary_sizes.append(value)
        elif key == "lines_per_chunk":
            lines_per_chunk = int(value)
        elif key == "error_rate":
            error_rate = float(value)


learning_sets_builder = Builder(action = randomise_wikipedia_articles)
vocabulary_files_builder = Builder(action = create_vocabularies)
trigram_models_builder = Builder(action = create_trigram_models)
real_word_vocabulary_builder = Builder(action = extract_real_word_vocabulary)
error_set_builder = Builder(action = create_error_sets)

env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'vocabulary_files' : vocabulary_files_builder, 'trigram_models' : trigram_models_builder, 'real_word_vocabulary_files' : real_word_vocabulary_builder, 'error_sets' : error_set_builder})

env.learning_sets([data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], data_directory + 'corpus.bz2')

env.Alias('learning_sets', [data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']])

env.vocabulary_files([data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes], [data_directory + 'training_set.bz2'])

env.Alias('vocabulary_files', [data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.trigram_models([data_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes], [data_directory + 'training_set.bz2'] + [data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.Alias('trigram_models', [data_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes])

env.real_word_vocabulary_files([data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes], [data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.Alias('real_word_vocabulary_files', [data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes])

env.error_sets([data_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes] + [data_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes], [data_directory + 'development_set.bz2'] + [data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes])

env.Alias('error_sets', [data_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes] + [data_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes])
