# L. Amber Wilcox-O'Hearn 2012
# SConstruct

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']

import codecs, bz2, gzip, random, subprocess, os, StringIO, filecmp, shutil

from math import ceil
from recluse import article_randomiser, vocabulary_generator, nltk_based_segmenter_tokeniser
from recluse.utils import *
from malaprop.error_insertion import RealWordVocabExtractor, RealWordErrorChannel

def randomise_articles(target, source, env):
    """
    target is a list of files corresponding to the training,
    development, and test sets.  source is a single bzipped file of
    articles.
    """
    article_file_obj = open_with_unicode(source[0].path, 'bzip2', 'r')
    train_file_obj = open_with_unicode(target[0].path, 'bzip2', 'w')
    devel_file_obj = open_with_unicode(target[1].path, 'bzip2', 'w')
    test_file_obj = open_with_unicode(target[2].path, 'bzip2', 'w')
    rand_obj = random.Random(7)
    ar = article_randomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, rand_obj, proportions)
    ar.randomise()
    return None

def create_language_models(target, source, env):

    # Split training set
    chunk_directory = data_directory + 'FILE_CHUNKS/'
    os.mkdir(chunk_directory)

    split_file_into_chunks(source[0].path, chunk_directory, lines_per_chunk)

    file_names = [chunk_directory + s for s in os.listdir(chunk_directory)]
    file_names_file_obj = open(chunk_directory + 'file_names', 'w')
    file_names_file_obj.writelines([s + '\n' for s in file_names])
    file_names_file_obj.close()

    # Create vocabularies:
    # For each n in vocabulary_sizes, gets the unigram counts from the
    # source files and puts the n thousand most frequent words in the
    # vocabulary file.
    vocab_gen = vocabulary_generator.VocabularyGenerator(file_names)
    for i in range(len(vocabulary_sizes)):
        size = int(1000*vocabulary_sizes[i])
        vocab_gen.generate_vocabulary(size, open_with_unicode(target[i].path, None, 'w'))

    # create trigram model:
    # Run srilm make/merge-batch-counts

    cwd = os.getcwd()
    bash_script_name = cwd + "/nltkbasedsegmentandtokenise.sh"
    bash_script_file_obj = open(bash_script_name, 'w')
    bash_script_file_obj.write("bzcat $1 | nltkbasedsegmentertokeniserrunner\n")
    bash_script_file_obj.close()
    os.chmod(bash_script_name, 0755)

    counts_directory = data_directory + 'TEMP_UPTO3_COUNTS_DIR/'
    srilm_make_batch_counts = subprocess.call(['make-batch-counts', chunk_directory + 'file_names', '1', bash_script_name, counts_directory])

    os.remove(bash_script_name)

    srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', counts_directory])
    for i in range(len(vocabulary_sizes)):
        size = vocabulary_sizes[i]
        vocabulary_file_name = data_directory + str(size) + 'K.vocab'
        merged_counts_file = [f for f in os.listdir(counts_directory) if f.endswith('.ngrams.gz')][0]
        trigram_model_name = data_directory + 'trigram_model_' + str(size) + 'K.arpa'
        assert target[len(vocabulary_sizes) + i].path == trigram_model_name, target[len(vocabulary_sizes) + i].path

        srilm_make_big_lm = subprocess.call(['make-big-lm', '-debug', '2', '-kndiscount3', '-unk', '-read', counts_directory + merged_counts_file, '-vocab', vocabulary_file_name, '-lm', trigram_model_name])

    # delete split files and counts
    shutil.rmtree(chunk_directory)
    shutil.rmtree(counts_directory)
    shutil.rmtree(cwd + '/biglm.kndir')
    [os.remove(f) for f in os.listdir(os.getcwd()) if f.startswith('biglm')]

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
            segmenter_tokeniser = nltk_based_segmenter_tokeniser.NLTKBasedSegmenterTokeniser(chunk)
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
        assert filecmp.cmp(data_directory + 'errors_at_0.2_0.05K_vocabulary.bz2', 'malaprop/test/data/errors_at_0.2_0.05K_vocabulary.bz2', shallow=False), "Test result errors_at_0.2_0.05K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'errors_at_0.2_0.5K_vocabulary.bz2', 'malaprop/test/data/errors_at_0.2_0.5K_vocabulary.bz2', shallow=False), "Test result errors_at_0.2_0.5K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'corrections_0.2_0.05K_vocabulary.bz2', 'malaprop/test/data/corrections_0.2_0.05K_vocabulary.bz2', shallow=False), "Test result corrections_0.2_0.05K_vocabulary.bz2 differs from expected."
        assert filecmp.cmp(data_directory + 'corrections_0.2_0.5K_vocabulary.bz2', 'malaprop/test/data/corrections_0.2_0.5K_vocabulary.bz2', shallow=False), "Test result corrections_0.2_0.5K_vocabulary.bz2 differs from expected."
        

    return None


# Get and set configuration:
# These are defaults that may be reset by the commandline:
data_directory = ''
vocabulary_sizes = []
lines_per_chunk = 100000
error_rate = .05
proportions = [.6,.2,.2]
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

# These are settings are derived from the above:
data_file = data_directory + 'corpus.bz2'
# -----

# SConstruct dependency information

learning_sets_builder = Builder(action = randomise_articles)
language_models_builder = Builder(action = create_language_models)
real_word_vocabulary_builder = Builder(action = extract_real_word_vocabulary)
error_set_builder = Builder(action = create_error_sets)

env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'language_models' : language_models_builder, 'real_word_vocabulary_files' : real_word_vocabulary_builder, 'error_sets' : error_set_builder})

env.learning_sets([data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], data_file)

env.Alias('learning_sets', [data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']])

env.language_models([data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes] + [data_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes], [data_directory + 'training_set.bz2'])

env.Alias('language_models', [data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes] + [data_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes])

env.real_word_vocabulary_files([data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes], [data_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.Alias('real_word_vocabulary_files', [data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes])

env.error_sets([data_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes] + [data_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes], [data_directory + 'development_set.bz2'] + [data_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes])

env.Alias('error_sets', [data_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes] + [data_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary.bz2' for size in vocabulary_sizes])
