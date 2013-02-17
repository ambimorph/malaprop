# L. Amber Wilcox-O'Hearn 2012
# SConstruct

# Ugly hack to avoid problem caused by ugly hack.
# See http://scons.tigris.org/issues/show_bug.cgi?id=2781
import sys
del sys.modules['pickle']


data_directory = 'data/'
corpus_directory = data_directory + 'corpora/WestburyLab.wikicorp.201004/'
training_chunk_path = corpus_directory + 'training_set_chunks/'
development_chunk_path = corpus_directory + 'development_set_chunks/'
language_model_directory = data_directory + 'language_models/WestburyLab.wikicorp.201004/'
error_set_directory = data_directory + 'error_sets/WestburyLab.wikicorp.201004/'
lines_per_srilm_chunk = 100000
num_development_chunks = 55
num_training_chunks = 167
vocabulary_sizes = [50, 100]
error_rate = .05

learning_sets_builder = Builder(action = randomise_wikipedia_articles)
vocabulary_files_builder = Builder(action = create_vocabularies)
trigram_models_builder = Builder(action = create_trigram_models)
real_word_vocabulary_builder = Builder(action = extract_real_word_vocabulary)
error_set_builder = Builder(action = create_error_sets)

env = Environment(BUILDERS = {'learning_sets' : learning_sets_builder, 'vocabulary_files' : vocabulary_files_builder, 'trigram_models' : trigram_models_builder, 'real_word_vocabulary_files' : real_word_vocabulary_builder, 'error_sets' : error_set_builder})

env.learning_sets([corpus_directory + set_name for set_name in ['training_set.bz2', 'development_set.bz2', 'test_set.bz2']], corpus_directory + 'WestburyLab.wikicorp.201004.txt.bz2')

env.vocabulary_files([language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes], [corpus_directory + 'training_set.bz2'])

env.trigram_models([language_model_directory + 'trigram_model_' + str(size) + 'K.arpa' for size in vocabulary_sizes], [corpus_directory + 'training_set.bz2'] + [language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.real_word_vocabulary_files([language_model_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes], [language_model_directory + str(size) + 'K.vocab' for size in vocabulary_sizes])

env.error_sets([error_set_directory + 'errors_at_' + str(error_rate) + '_' + str(size) + 'K_vocabulary_' + development_file_name + '.bz2' for size in vocabulary_sizes for development_file_name in os.listdir(development_chunk_path)] + [error_set_directory + 'corrections_' + str(error_rate) + '_' + str(size) + 'K_vocabulary_' + development_file_name + '.bz2' for size in vocabulary_sizes for development_file_name in os.listdir(development_chunk_path)], [corpus_directory + 'development_set.bz2'] + [language_model_directory + str(size) + 'K.real_word_vocab' for size in vocabulary_sizes])
