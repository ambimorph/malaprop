# L. Amber Wilcox-O'Hearn 2012
# SConstruct

import codecs, bz2, random, subprocess
import WikipediaArticleRandomiser

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

def split_training_set_into_chunks(target, source, env):
    "We take the training set and split it into files of 100000 lines each so that srilm can make counts without choking.  It also needs a list of the names of the resulting files.  This function will delete the source file to save space. "
    lines_per_chunk = 100000
    training_file_obj = open_with_unicode_bzip2(source[0], 'r')
    current_line_number = 0
    current_file_number = 0
    while current_file_number < num_chunks:
        print "file number ", current_file_number, " line number ", current_line_number
        current_file_obj = open_with_unicode_bzip2(target[current_file_number], 'w')
        current_file_obj.write(training_file_obj.readline())
        current_line_number += 1
        while current_line_number % lines_per_chunk > 0:
            print "file number ", current_file_number, " line number ", current_line_number
            current_file_obj.write(training_file_obj.readline())
            current_line_number += 1
        current_file_number += 1
    file_names_file_obj = open(target[-1].path, 'w')
    for file_name in target[:-1]:
        file_names_file_obj.write(file_name.path + '\n')
    return None

def create_vocabularies(target, source, env):
    "Gets the unigram counts from the source files and puts the n most frequent words in the vocabulary file."
    return None

data_directory = '../../data/'
corpus_directory = data_directory + 'corpora/WestburyLab.wikicorp.201004/'
randomised_wikipedia_articles_builder = Builder(action = randomise_wikipedia_articles)
split_training_set_into_chunks_builder = Builder(action = split_training_set_into_chunks)
env = Environment(BUILDERS = {'learning_sets' : randomised_wikipedia_articles_builder, 'training_chunks' : split_training_set_into_chunks_builder})
env.learning_sets([corpus_directory + x for x in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], corpus_directory + 'WestburyLab.wikicorp.201004.txt.bz2')
num_chunks = 167
env.training_chunks([corpus_directory + 'training_set_chunks/training_set_chunk_' + '%03d' % num + '.bz2' for num in range(num_chunks)] + [corpus_directory + 'training_set_chunks/file_names'], [corpus_directory + 'training_set.bz2'])




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
