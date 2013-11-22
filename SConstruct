# SConstruct

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']

import codecs, bz2, gzip, random, subprocess, os, StringIO, filecmp, shutil, json, cPickle

from recluse import article_selector, vocabulary_generator, nltk_based_segmenter_tokeniser
from recluse.utils import *
from DamerauLevenshteinDerivor import cderivor
from BackOffTrigramModel.BackOffTrigramModelPipe import BackOffTMPipe
from malaprop.error_insertion import real_word_vocabulary_extractor
from malaprop.error_insertion.confusion_set_channel import *
from malaprop.error_insertion.real_word_error_inserter import *
from malaprop.choosing.trigram_based_chooser import *
from malaprop.correction.corrector import *
from malaprop.evaluation.adversarial_evaluator import *
from malaprop.evaluation.correction_evaluator import *

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
    and puts the n thousand most frequent words of frequency at least
    2 in the vocabulary file.
    """

    vocab_gen = vocabulary_generator.VocabularyGenerator([source[0].path])
    n = int(1000*vocabulary_size)
    vocab_gen.generate_vocabulary(open_with_unicode(target[0].path, None, 'w'), size=n, min_frequency=2)

def create_segmenter_tokeniser(target, source, env):

    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(bz2.BZ2File(source[0].path, 'r'))
    cPickle.dump(segmenter_tokeniser.sbd, open(target[0].path, 'w'))

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
    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(punkt_obj=cPickle.load(open(source[0].path, 'r')))
    rwei = RealWordErrorInserter(segmenter_tokeniser, vocabulary, error_channel)
    text = open_with_unicode(source[2].path, 'bzip2', 'r').read()
    sentence_id += rwei.corrupt(text, file_dict, correction_task, adversarial_task, sentence_id)

    for f in file_dict.values():
        f.close()

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

    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(punkt_obj=cPickle.load(open(source[0].path, 'r')))
    path_to_botmp = subprocess.check_output(['which', 'BackOffTrigramModelPipe']).strip()
    arpa_file_name = source[1].path
    botmp = BackOffTMPipe(path_to_botmp, arpa_file_name)

    chooser = TrigramBasedChooser(segmenter_tokeniser, botmp.trigram_probability)
    choices_file = open_with_unicode(target[0].path, 'bzip2', 'w')
    if TEST:
        line_count = 0
    for line in open_with_unicode(source[2].path, 'bzip2', 'r'):
        pair = json.loads(line)
        choice = chooser.choose(pair)
        choices_file.write(unicode(choice))
        if TEST:
            if line_count > max_lines: break
            line_count += 1

def evaluate_chooser(target, source, env):

    acc, errs = report_accuracy_and_errors(open_with_unicode(source[0].path, 'bzip2', 'r'), open_with_unicode(source[1].path, 'bzip2', 'r'), open_with_unicode(source[2].path, 'bzip2', 'r'))
    evaluation_file = open_with_unicode(target[0].path, None, 'w')
    evaluation_file.write('Accuracy %f\n' % acc)
    evaluation_file.write('Errors:\n')
    for err in errs:
        evaluation_file.write(err + '\n')

def propose(target, source, env):

    segmenter_tokeniser = NLTKBasedSegmenterTokeniser(punkt_obj=cPickle.load(open(source[0].path, 'r')))
    d = cderivor.Derivor(source[1].path)
    vocabulary, symbols = vocabulary_file_to_sets(open_with_unicode(source[1].path, None, 'r'))
    def confusion_set_function(token):
        if token in vocabulary:
            return d.variations(token)
        return []
    path_to_botmp = subprocess.check_output(['which', 'BackOffTrigramModelPipe']).strip()
    arpa_file_name = source[2].path
    botmp = BackOffTMPipe(path_to_botmp, arpa_file_name)
    hmm = HMM(confusion_set_function, botmp, 1-alpha, viterbi_type, prune_to, backoff_threshold)
    proposer = Corrector(segmenter_tokeniser, hmm)

    proposed_file = open_with_unicode(target[0].path, 'bzip2', 'w')
    sentence_id = 0
    if TEST:
        line_count = 0
    for line in open_with_unicode(source[3].path, 'bzip2', 'r'):
        if sentence_id % 100 == 0: print '.',
        correction = proposer.correct(line)
        if correction != []:
            proposed_file.write(json.dumps([sentence_id, correction]) + '\n')
        sentence_id +=1
        if TEST:
            if line_count > max_lines: break
            line_count += 1
    print 'Corrected', sentence_id, 'sentences'
        
def evaluate_proposer(target, source, env):
    
    ce = CorrectionEvaluator()
    ce.process_all_corrections(bz2.BZ2File(source[0].path, 'r'), bz2.BZ2File(source[1].path, 'r'))
    evaluation_file = open(target[0].path, 'w')
    report_dict = ce.report(corrections_report_size)
    evaluation_file.write('Detection Precision: %f\n' % report_dict['Detection Precision'])
    evaluation_file.write('Detection Recall: %f\n' % report_dict['Detection Recall'])
    evaluation_file.write('Detection F-measure: %f\n' % report_dict['Detection F-measure'])
    evaluation_file.write('Correction Precision: %f\n' % report_dict['Correction Precision'])
    evaluation_file.write('Correction Recall: %f\n' % report_dict['Correction Recall'])
    evaluation_file.write('Correction F-measure: %f\n' % report_dict['Correction F-measure'])
    evaluation_file.write('False Negatives: ')
    for el in report_dict['False Negative']:
        evaluation_file.write('%s: %d\n' % (el[0], el[1]))
    evaluation_file.write('False Positives: ')
    for el in report_dict['False Positive']:
        evaluation_file.write('%s: %d\n' % (el[0], el[1]))
    evaluation_file.write('True Positives: ')
    for el in report_dict['True Positive']:
        evaluation_file.write('%s: %d\n' % (el[0], el[1]))
    evaluation_file.write('Miscorrections: ')
    for el in report_dict['Detection True Positive, Correction False Negative, Correction False Positive']:
        evaluation_file.write('%s: %d\n' % (el[0], el[1]))
                          


# Get and set configuration:
# These are defaults that may be reset by the commandline:
new_corpus = False
data_directory = ''
experiment_size = 0
vocabulary_size = 0
error_rate = 0
proportions = [.6,.2,.2]
correction_task = False
adversarial_task = False
alpha = 1 - error_rate
viterbi_type = 2
prune_to = None
backoff_threshold = None
verbosity = True
corrections_report_size = 0
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
    max_lines = 100
    correction_task = True
    adversarial_task = True
    alpha = 1 - error_rate
    corrections_report_size = 5

elif [x for x in ARGLIST if x[0] == "replicate"]:
    vocabulary_size = 100
    error_rate = .05
    correction_task = True
    adversarial_task = True
    corrections_report_size = 20

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
    elif key == alpha:
        alpha = float(value)
    elif key == viterbi_type:
        viterbi_type = int(value)
    elif key == prune_to:
        viterbi_type = int(prune_to)
    elif key == backoff_threshold:
        backoff_threshold = float(value)
    elif key == verbosity:
        verbosity = int(value)
    elif key == corrections_report_size:
        corrections_report_size = int(value)
        

# These are settings are derived from the above:
data_file = data_directory + 'corpus.bz2'
error_set_targets = []
if correction_task: error_set_targets += ['corrupted', 'corrections']
if adversarial_task: error_set_targets += ['adversarial', 'key']
# -----

# SConstruct dependency information

vocabulary_builder = Builder(action = create_vocabulary)
segmenter_tokeniser_builder = Builder(action = create_segmenter_tokeniser)
real_word_vocabulary_builder = Builder(action = extract_real_word_vocabulary)
error_set_builder = Builder(action = create_error_sets)
trigram_model_builder =Builder(action = create_trigram_model)
trigram_choices_builder = Builder(action = choose)
trigram_proposed_corrections_builder = Builder(action = propose)
chooser_evaluation_builder = Builder(action = evaluate_chooser)
proposer_evaluation_builder = Builder(action = evaluate_proposer)

builders = {'vocabulary' : vocabulary_builder, 'segmenter_tokeniser' : segmenter_tokeniser_builder, 'real_word_vocabulary' : real_word_vocabulary_builder, 'error_sets' : error_set_builder, 'trigram_model' : trigram_model_builder, 'trigram_choices' : trigram_choices_builder, 'trigram_proposed_corrections' : trigram_proposed_corrections_builder, 'chooser_evaluation' : chooser_evaluation_builder, 'proposer_evaluation': proposer_evaluation_builder}

if new_corpus:

    learning_sets_builder = Builder(action = randomise_articles)
    builders['learning_sets'] = learning_sets_builder
    env.learning_sets([data_directory + f for f in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2', 'article_index']], data_file)
    env.Alias('learning_sets', [data_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']])

env = Environment(BUILDERS = builders)

env.vocabulary([data_directory + str(vocabulary_size) + 'K_vocabulary'], [data_directory + 'training_set.bz2'])
env.Alias('vocabulary', [data_directory + str(vocabulary_size) + 'K_vocabulary'])

env.segmenter_tokeniser([data_directory + 'segmenter_tokeniser.pkl'], [data_directory + 'training_set.bz2'])
env.Alias('segmenter_tokeniser', [data_directory + 'segmenter_tokeniser.pkl'])

env.real_word_vocabulary([data_directory + 'real_word_vocabulary'], [data_directory + str(vocabulary_size) + 'K_vocabulary'])
env.Alias('real_word_vocabulary', [data_directory +'real_word_vocabulary'])

env.error_sets([data_directory + x + '_error_rate_' + str(error_rate) + '.bz2' for x in error_set_targets], [data_directory + 'segmenter_tokeniser.pkl', data_directory + 'real_word_vocabulary', data_directory + 'development_set.bz2'])
env.Alias('error_sets', [data_directory + x + '_error_rate_' + str(error_rate) + '.bz2' for x in error_set_targets])

env.trigram_model([data_directory + str(vocabulary_size) + 'K_trigram_model.arpa'], [data_directory + 'training_set.bz2', data_directory + str(vocabulary_size) + 'K_vocabulary'])
env.Alias('trigram_model', [data_directory + str(vocabulary_size) + 'K_trigram_model.arpa'])

env.trigram_choices([data_directory + 'trigram_choices_error_rate_' + str(error_rate) + '.bz2'], [data_directory + 'segmenter_tokeniser.pkl', data_directory + str(vocabulary_size) + 'K_trigram_model.arpa', data_directory + 'adversarial_error_rate_' + str(error_rate) + '.bz2'])
env.Alias('trigram_choices', [data_directory + 'trigram_choices.bz2'])

subdirectory = data_directory + 'alpha_' + str(alpha) + '_viterbi_' + str(viterbi_type) + '_backoff_' + str(backoff_threshold) + '/'
if not os.path.exists(subdirectory): os.mkdir(subdirectory)

env.trigram_proposed_corrections([subdirectory + 'trigram_proposed_corrections_error_rate_'  + str(error_rate) + '.bz2'], [data_directory + 'segmenter_tokeniser.pkl', data_directory +  'real_word_vocabulary', data_directory + str(vocabulary_size) + 'K_trigram_model.arpa', data_directory + 'corrupted_error_rate_' + str(error_rate) + '.bz2'])
env.Alias('trigram_proposed_corrections', [subdirectory + 'trigram_proposed_corrections_error_rate_' + str(error_rate) + '.bz2'])

env.chooser_evaluation([data_directory + 'evaluation_trigram_choices_error_rate_' +  str(error_rate)], [data_directory + 'key_error_rate_' + str(error_rate) + '.bz2', data_directory + 'trigram_choices_error_rate_' + str(error_rate) + '.bz2', data_directory + 'adversarial_error_rate_' + str(error_rate) + '.bz2'])
env.Alias('chooser_evaluation', [data_directory + 'evaluation_trigram_choices_error_rate_' +  str(error_rate)])

env.proposer_evaluation([subdirectory + 'evaluation_trigram_proposed_corrections_error_rate_' +  str(error_rate)], [data_directory + 'corrections_error_rate_' + str(error_rate) + '.bz2', subdirectory + 'trigram_proposed_corrections_error_rate_' + str(error_rate) + '.bz2'])
env.Alias('proposer_evaluation', [subdirectory + 'evaluation_trigram_proposed_corrections_error_rate_' +  str(error_rate)])

