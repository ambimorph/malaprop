Malaprop

Author: L. Amber Wilcox-O'Hearn

Contact: amber@cs.toronto.edu

Released under the GNU AFFERO GENERAL PUBLIC LICENSE, see COPYING file for details.

============
Introduction
============
Malaprop is a project involving transformations of natural text that result in some words being replaced by real-word near neighbours.  

Malaprop is written in the spirit of the adversarial evaluation paradigm for natural language processing proposed by Noah Smith [http://arxiv.org/abs/1207.0245].  Please see http://subsymbol.org for discussion.

This first version includes code to 

(1) Divide a corpus of text articles (e.g. Wikipedia) into training, development, and test sets.

(2) Generate trigram models from a training set.

(3) Create a corpus of real-word errors embedded in a copy of the development set along with a separate index to the errors and their corrections.

It acts as a noisy channel, randomly inserting Damerau-Levenshtein [http://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance] errors at the character level as a word is passed through. If the resulting string is a *real word* — that is, a sufficiently frequent word in the original corpus — the new word replaces the original.

============
Dependencies
============
Malaprop requires:

Python, Scons, NLTK, and SRILM.

It was tested under the following versions:

* Ubuntu 12.04.2 LTS
* Python 2.7.3
* SCons v2.1.0.r5357
* NLTK 2.0b9
* SRILM 1.5.5

=================
Running the tests
=================
Unit tests: Run 

::

 $ python -m unittest discover

SCons test:
Create a directory DIR for testing, and copy or link test_data/Wikipedia_small_subset.bz2 as corpus.bz2.

::

 $ ln -s ../test_data/Wikipedia_small_subset.bz2 DIR/corpus.bz2

Run 

::

 $ scons data_directory=DIR test=1

=================================
Running Malaprop on your own data
=================================
Create a directory DIR for testing, and copy or link your b2zipped corpus as corpus.bz2.
Run 

::

 $ scons data_directory=DIR variables target

Current possible targets: 

* learning_sets
    * DIR must contain corpus.bz2, which consists of articles divided by the following line:
        "---END.OF.DOCUMENT---"
    * no variables 

    * -> divided into 60-20-20% training, development, and test

* vocabulary_files:
    * DIR must contain training_set.bz2 OR dependencies for learning_sets
    * one or more variables vocabulary_size=n
    * lines_per_chunk=n (defaults to 100000)

    * -> nK.vocab for n in vocabulary_size

* trigram_models:
    * variables vocabulary_size=n 
    * DIR must contain a vocabulary file nK.vocab for n in vocabulary_size
      OR 
    * dependencies met for vocabulary_files

    * -> trigram_model_nK.arpa for n in vocabulary_size

* real_word_vocabulary_files
    * variables vocabulary_size=n 
    * DIR must contain nK.vocab for each n in vocabulary_size
      OR
    * dependencies met for vocabulary_files

    * -> nK.real_word_vocab for n in vocabulary_size

* error_sets
    * DIR must contain development_set.bz2 or dependencies met for learning_sets
    * lines_per_chunk=n (defaults to 100000)
    * error_rate in {0,1} (defaults to .05)
    * variables vocabulary_size=n
    * DIR must contain nK.real_word_vocab for n in vocabulary_size
      OR 
    * dependencies met for real_word_vocabulary_files

    * -> errors_at_e_nK_vocabulary.bz2, corrections_e_nK_vocabulary.bz2 for e=error_rate for n in vocabulary_size

Note: vocabulary_size is given in thousands.

================
Acknowledgements
================
Zooko Wilcox-O'Hearn contributed endless hours to engineering and debuggery advice.
