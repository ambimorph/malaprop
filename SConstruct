# L. Amber Wilcox-O'Hearn 2012
# SConstruct

import codecs, bz2, random, subprocess

from code.preprocessing import WikipediaArticleRandomiser
from code.language_modelling import vocabulary_cutter

def open_with_unicode_bzip2(file_name, mode):
    assert mode in ['r', 'w']
    if mode == 'r':
        return codecs.getreader('utf-8')(bz2.BZ2File(file_name.path, mode))
    elif mode == 'w':
        return codecs.getwriter('utf-8')(bz2.BZ2File(file_name.path, mode))

def randomise_wikipedia_articles(target, source, env):
    "target is a list of files corresponding to the training, development, and test sets.  source is a single bzipped file of wikipedia articles."
    article_file_obj = open_with_unicode_bzip2(source[0], 'r')
    train_file_obj = open_with_unicode_bzip2(target[0], 'w')
    devel_file_obj = open_with_unicode_bzip2(target[1], 'w')
    test_file_obj = open_with_unicode_bzip2(target[2], 'w')
    rand_obj = random.Random(7)
    ar = WikipediaArticleRandomiser.Randomiser(article_file_obj, train_file_obj, devel_file_obj, test_file_obj, rand_obj)
    ar.randomise()
# Somewhere, perhaps here, we ought to assert that the results give the following md5sums:
# 72c01f8951f8968788bea57034e121a0  training_set.bz2
# 19d502cfdedc5517e4b2a808171f9ac4  development_set.bz2
# e683df17e81a5732605eefc9618d0403  test_set.bz2
    return None

def create_vocabularies(target, source, env):
"For each n in vocabulary_sizes, gets the unigram counts from the source files and puts the n most frequent words in the vocabulary file."

    # Split training set into chunks.
    # We take the training set and split it into files of 100000 lines each so that srilm can make counts without choking.
    # It also needs a list of the names of the resulting files.

    lines_per_chunk = 100000
    training_file_obj = open_with_unicode_bzip2(source[0], 'r')
    chunk_path = corpus_directory + 'training_set_chunks/'
    file_names_file_obj = open(chunk_path + 'file_names', 'w')
    current_line_number = 0
    current_file_number = 0
    while current_file_number < num_chunks:
        current_filename = chunk_path + 'training_set_chunk_%03d' % current_file_number
        file_names_file_obj.write(current_filename + '\n')
        current_file_obj = open_with_unicode_bzip2(current_filename, 'w')
        current_file_obj.write(training_file_obj.readline())
        current_line_number += 1
        while current_line_number % lines_per_chunk > 0:
            current_file_obj.write(training_file_obj.readline())
            current_line_number += 1
        current_file_number += 1

    # Run srilm make/merge-batch-counts

    srilm_make_batch_counts = subprocess.Popen(['make-batch-counts', chunk_path + 'file_names', '1', 'code/preprocessing/nltksegmentandtokenise.sh', language_model_directory + 'temp_counts_directory', '-write-order 1'])
    srilm_merge_batch_counts = subprocess.Popen(['merge-batch-counts', language_model_directory + 'temp_counts_directory'])

    # Make vocabularies

    # Delete count files

    return None

data_directory = 'data/'
corpus_directory = data_directory + 'corpora/WestburyLab.wikicorp.201004/'
language_model_directory = data_directory + 'language_models/WestburyLab.wikicorp.201004/'
num_chunks = 167
vocabulary_sizes = [50, 100]

learning_sets_builder = Builder(action = randomise_wikipedia_articles)
vocabulary_files_builder = Builder(action = create_vocabularies)

env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'vocabulary_files' : vocabulary_files_builder})

env.learning_sets([corpus_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], corpus_directory + 'WestburyLab.wikicorp.201004.txt.bz2')

env.vocabulary_files([language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes], [corpus_directory + 'training_set.bz2'])




# def build_language_model(target, source, env):
#     subprocess.Popen(['make-big-lm', '-kndiscount', '-unk', '-read', source[0], '-vocab', source[1], '-lm', target])
#     return None
# bld_lm = Builder(action = build_language_model)
# env = Environment(BUILDERS = {'LM' : bld_lm})
# env.LM(
#env.LM('corpora_and_models/westbury_wikipedia_2010_04/training_set/trigram_model_50K.arpa', ['corpora_and_models/westbury_wikipedia_2010_04/training_set/counts_upto3/*ngrams.gz', 'corpora_and_models/westbury_wikipedia_2010_04/training_set/50K.vocab'])



# env.Command('corpora_and_models/westbury_wikipedia_2010_04/training_set/trigram_model_50K.arpa', ['corpora_and_models/westbury_wikipedia_2010_04/training_set/counts_upto3/*ngrams.gz', 'corpora_and_models/westbury_wikipedia_2010_04/training_set/50K.vocab'], "make-big-lm -kndiscount -unk -read $SOURCE[0] -vocab $SOURCE[1] -lm $TARGET")

#env.Command('test_scons.arpa', ['/*ngrams.gz', 'corpora_and_models/westbury_wikipedia_2010_04/training_set/50K.vocab'], "make-big-lm -kndiscount -unk -read $SOURCE[0] -vocab $SOURCE[1] -lm $TARGET")

#env.Command(['corpora_and_models/westbury_wikipedia_2010_04/training_set/train.bz2', 'corpora_and_models/westbury_wikipedia_2010_04/development_set/devel.bz2', 'corpora_and_models/westbury_wikipedia_2010_04/test_set/test.bz2'], ['corpora_and_models/westbury_wikipedia_2010_04/original.bz2'], "bzcat $SOURCE | python language_modelling_scripts/wikipedia_article_randomiser.py")
