# SConstruct

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']

import codecs, bz2, gzip, random, subprocess, os, StringIO, filecmp, shutil, json

from math import ceil
from recluse import article_selector, vocabulary_generator, nltk_based_segmenter_tokeniser
from recluse.utils import *
from DamerauLevenshteinDerivor import cderivor
from BackOffTrigramModel.BackOffTrigramModelPipe import BackOffTMPipe
from malaprop.error_insertion import real_word_vocabulary_extractor
from malaprop.error_insertion.confusion_set_channel import *
from malaprop.error_insertion.real_word_error_inserter import *
from malaprop.choosing.trigram_based_chooser import *

def randomise_articles(target, source, env):
    """
    target is a list of files corresponding to the training,
    development, and test sets.  source is a single bzipped file of
    articles.
    """
    separator = '\---END\.OF\.DOCUMENT---'
    total_article_count = int(subprocess.check_output(['bzgrep', '-c', '-E', separator, source[0].path]))
    article_file_obj = open_with_unicode(source[0].path, 'bzip2', 'r')
    train_file_obj = open_with_unicode(target[0].path, 'bzip2', 'w')
    devel_file_obj = open_with_unicode(target[1].path, 'bzip2', 'w')
    test_file_obj = open_with_unicode(target[2].path, 'bzip2', 'w')
    index_file_obj = open_with_unicode(target[3].path, None, 'w')
    rand_obj = random.Random(7)
    selector = article_selector.ArticleSelector(article_file_obj, train_file_obj, devel_file_obj, test_file_obj)
    index = selector.select_and_distribute(rand_obj, total_article_count, experiment_size, proportions)
    index_file_obj.write(json.dumps(index)+'\n')
    return None

def create_vocabulary(target, source, env):

    """
    Create vocabulary: Gets the unigram counts from the source files
    and puts the n thousand most frequent words in the vocabulary
    file.
    """

    vocab_gen = vocabulary_generator.VocabularyGenerator([source[0].path])
    size = int(1000*vocabulary_size)
    vocab_gen.generate_vocabulary(size, open_with_unicode(target[0].path, None, 'w'))

def extract_real_word_vocabulary(target, source, env):

    vocabulary_file_obj = open(source[0].path, 'r')
    real_word_vocabulary_file_obj = open(target[0].path, 'w')
    extractor = real_word_vocabulary_extractor.RealWordVocabExtractor(vocabulary_file_obj, real_word_vocabulary_file_obj)
    extractor.extract_real_words()
    return

def vocabulary_file_to_sets(vocabulary_file):

    vocabulary = set([])
    symbols = set([])
    for line in vocabulary_file:
        token = line.strip()
        vocabulary.add(token)
        for s in token: symbols.add(s)
    return vocabulary, list(symbols)
    

def create_error_sets(target, source, env):

    assert correction_task or adversarial_task

    rand_obj = random.Random(33)
    derivor = cderivor.Derivor(source[1].path)
    error_channel = ConfusionSetChannel(rand_obj, error_rate, derivor.variations, None)

    file_dict = {}
    if correction_task:
        file_dict['corrupted'] = bz2.BZ2File(target[0].path, 'w')
        file_dict['corrections'] = bz2.BZ2File(target[1].path, 'w')
        if adversarial_task:
            file_dict['adversarial'] = bz2.BZ2File(target[2].path, 'w')
            file_dict['key'] = bz2.BZ2File(target[3].path, 'w')
    else:
        file_dict['adversarial'] = bz2.BZ2File(target[0].path, 'w')
        file_dict['key'] = bz2.BZ2File(target[1].path, 'w')
    
    sentence_id = 0
    vocabulary, symbols = vocabulary_file_to_sets(open_with_unicode(source[1].path, None, 'r'))
    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(bz2.BZ2File(source[0].path, 'r'))
    rwei = RealWordErrorInserter(segmenter_tokeniser, vocabulary, error_channel)
    sentence_id += rwei.corrupt(segmenter_tokeniser.text, file_dict, correction_task, adversarial_task, sentence_id)

    for f in file_dict.values():
        f.close()


    # Regression tests
#    if TEST:
#        assert filecmp.cmp(data_directory + 'corrupted_error_rate_0.1_2K_vocabulary.bz2', 'malaprop/test/data/corrupted_error_rate_0.1_2K_vocabulary.bz2', shallow=False), "Test result corrupted_error_rate_0.1_2K_vocabulary.bz2 differs from expected."
#        assert filecmp.cmp(data_directory + 'corrections_error_rate_0.1_2K_vocabulary.bz2', 'malaprop/test/data/corrections_error_rate_0.1_2K_vocabulary.bz2', shallow=False), "Test result corrections_error_rate_0.1_2K_vocabulary.bz2 differs from expected."
#        assert filecmp.cmp(data_directory + 'adversarial_error_rate_0.1_2K_vocabulary.bz2', 'malaprop/test/data/adversarial_error_rate_0.1_2K_vocabulary.bz2', shallow=False), "Test result adversarial_error_rate_0.1_2K_vocabulary.bz2 differs from expected."
#        assert filecmp.cmp(data_directory + 'key_error_rate_0.1_2K_vocabulary.bz2', 'malaprop/test/data/key_error_rate_0.1_2K_vocabulary.bz2', shallow=False), "Test result key_error_rate_0.1_2K_vocabulary.bz2 differs from expected."

    return None

def create_trigram_model(target, source, env):

    # Run srilm make/merge-batch-counts

    file_names_filename = data_directory + 'file_names'
    file_names_file_obj = open(file_names_filename, 'w')
    file_names_file_obj.write(source[0].path)
    file_names_file_obj.close()

    cwd = os.getcwd()
    bash_script_name = cwd + "/nltkbasedsegmentandtokenise.sh"
    bash_script_file_obj = open(bash_script_name, 'w')
    bash_script_file_obj.write("bzcat $1 | nltkbasedsegmentertokeniserrunner\n")
    bash_script_file_obj.close()
    os.chmod(bash_script_name, 0755)

    counts_directory = data_directory + 'TEMP_UPTO3_COUNTS_DIR/'
    srilm_make_batch_counts = subprocess.call(['make-batch-counts', file_names_filename, '1', bash_script_name, counts_directory])

    os.remove(file_names_filename)
    os.remove(bash_script_name)

    srilm_merge_batch_counts = subprocess.call(['merge-batch-counts', counts_directory])
    merged_counts_file = [f for f in os.listdir(counts_directory) if f.endswith('.ngrams.gz')][0]
    srilm_make_big_lm = subprocess.call(['make-big-lm', '-debug', '2', '-kndiscount3', '-unk', '-read', counts_directory + merged_counts_file, '-vocab', source[1].path, '-lm', target[0].path])

    # delete counts
    shutil.rmtree(counts_directory)
    shutil.rmtree(cwd + '/biglm.kndir')
    [os.remove(f) for f in os.listdir(os.getcwd()) if f.startswith('biglm')]

    return None

def choose(target, source, env):

    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(bz2.BZ2File(source[0].path, 'r'))
    path_to_botmp = subprocess.check_output(['which', 'BackOffTrigramModelPipe']).strip()
    arpa_file_name = source[1].path
    botmp = BackOffTMPipe(path_to_botmp, arpa_file_name)

    chooser = TrigramBasedChooser(segmenter_tokeniser, botmp.trigram_probability)
    choices_file = open_with_unicode(target[0].path, 'bzip2', 'w')
    for line in open_with_unicode(source[2].path, 'bzip2', 'r'):
        pair = json.loads(line)
        choice = chooser.choose(pair)
        choices_file.write(unicode(choice))
        


# Get and set configuration:
# These are defaults that may be reset by the commandline:
new_corpus = False
data_directory = ''
experiment_size = 20
vocabulary_size = 0.5
error_rate = .05
proportions = [.6,.2,.2]
correction_task = False
adversarial_task = False
TEST = False

try:
    data_directory = [x[1] for x in ARGLIST if x[0] == "data_directory"][0] + '/'
except:
    print "Usage: scons data_directory=DIR variables target"
    raise Exception

if [x for x in ARGLIST if x[0] == "test"]:
    TEST = True
    vocabulary_size = 2
    error_rate = .1
    correction_task = True
    adversarial_task = True

elif [x for x in ARGLIST if x[0] == "replicate"]:
    vocabulary_size = 100
    error_rate = .05
    correction_task = True
    adversarial_task = True

else:
    for key, value in ARGLIST:
        if key == "new_corpus":
            new_corpus = bool(value)
        elif key == "experiment_size":
            experiment_size = int(value)
        elif key == "vocabulary_size":
            vocabulary_size = float(value)
        elif key == "error_rate":
            error_rate = float(value)
        elif key == "correction_task":
            correction_task = True
        elif key == "adversarial_task":
            adversarial_task = True

# These are settings are derived from the above:
data_file = data_directory + 'corpus.bz2'
error_set_targets = []
if correction_task: error_set_targets += ['corrupted', 'corrections']
if adversarial_task: error_set_targets += ['adversarial', 'key']
# -----

# SConstruct dependency information

vocabulary_builder = Builder(action = create_vocabulary)
real_word_vocabulary_builder = Builder(action = extract_real_word_vocabulary)
error_set_builder = Builder(action = create_error_sets)
trigram_model_builder =Builder(action = create_trigram_model)
trigram_choices_builder = Builder(action = choose)

if new_corpus:

    learning_sets_builder = Builder(action = randomise_articles)
    env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'vocabulary' : vocabulary_builder, 'real_word_vocabulary_files' : real_word_vocabulary_builder, 'error_sets' : error_set_builder, 'trigram_model' : trigram_model_builder, 'trigram_choices' : trigram_choices_builder})
    env.learning_sets([data_directory + f for f in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2', 'article_index']], data_file)
    env.Alias('learning_sets', [data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']])

else:
    env = Environment(BUILDERS = {'vocabulary' : vocabulary_builder, 'real_word_vocabulary_files' : real_word_vocabulary_builder, 'error_sets' : error_set_builder, 'trigram_model' : trigram_model_builder, 'trigram_choices' : trigram_choices_builder})


env.vocabulary([data_directory + str(vocabulary_size) + 'K.vocab'], [data_directory + 'training_set.bz2'])
env.Alias('vocabulary', [data_directory + str(vocabulary_size) + 'K.vocab'])

env.real_word_vocabulary_files([data_directory + str(vocabulary_size) + 'K.real_word_vocab'], [data_directory + str(vocabulary_size) + 'K.vocab'])
env.Alias('real_word_vocabulary_files', [data_directory + str(vocabulary_size) + 'K.real_word_vocab'])

env.error_sets([data_directory + x + '_error_rate_' + str(error_rate) + '_' + str(vocabulary_size) + 'K_vocabulary.bz2' for x in error_set_targets], [data_directory + 'development_set.bz2', data_directory + str(vocabulary_size) + 'K.real_word_vocab'])
env.Alias('error_sets', [data_directory + x + '_error_rate_' + str(error_rate) + '_' + str(vocabulary_size) + 'K_vocabulary.bz2' for x in error_set_targets])

env.trigram_model([data_directory + 'trigram_model_' + str(vocabulary_size) + 'K.arpa'], [data_directory + 'training_set.bz2', data_directory + str(vocabulary_size) + 'K.vocab'])
env.Alias('trigram_model', ['trigram_model_' + str(vocabulary_size) + 'K.arpa'])

env.trigram_choices([data_directory + 'trigram_choices_error_rate_' + str(error_rate) + '_' + str(vocabulary_size) + 'K_vocabulary.bz2'], [data_directory + 'training_set.bz2', data_directory + 'trigram_model_' + str(vocabulary_size) + 'K.arpa', data_directory + 'adversarial' + '_error_rate_' + str(error_rate) + '_' + str(vocabulary_size) + 'K_vocabulary.bz2'])
env.Alias('trigram_choices', [data_directory + 'trigram_choices_error_rate_' + str(error_rate) + '_' + str(vocabulary_size) + 'K_vocabulary.bz2'])


