Malaprop

Author: L. Amber Wilcox-O'Hearn

Contact: amber@cs.toronto.edu

Released under the GNU AFFERO GENERAL PUBLIC LICENSE, see COPYING file for details.

============
Introduction
============
Malaprop is a project involving transformations of natural text that result in some words being replaced by real-word near neighbours.  

Malaprop is written in the spirit of `the adversarial evaluation paradigm for natural language processing proposed by Noah Smith`_.  Please see http://subsymbol.org for discussion.

The damerau_levenshtein_channel module emulates a noisy channel, randomly inserting `Damerau-Levenshtein`_  errors at the character level as a word is passed through. If the resulting string is a *real word* — that is, a sufficiently frequent word in the original corpus — the new word replaces the original.

This version includes code to 

(1) Divide a corpus of text articles (e.g. Wikipedia) into training, development, and test sets (from recluse).

(2) Generate trigram models from a training set by wrapping some specific calls to the srilm tool-kit over text segmented and tokenised using a customised version of the NLTK sentence segmenter.

(3) Create a correction task: a corpus of real-word errors embedded in a copy of the development set along with a separate index to the errors and their corrections.

(4) Create an original text recognition task for adversarial evaluation: a set of pairs of sentences, one original, and one corrupted, and a key to ientify them.


*Reproducibility* is prioritised, so projects are completely built using SCons.

============
Dependencies
============
Malaprop requires:

Python, recluse, SCons, NLTK, and SRILM.

It was tested under the following versions:

* Ubuntu 12.04.2 LTS
* Python 2.7.3
* recluse 0.2.4
* SCons v2.1.0.r5357
* NLTK 2.0b9
* SRILM 1.5.5

=================
Running the tests
=================
Unit tests: Run 

::

 $ python -m unittest discover

This should find 14 tests.

SCons test:
Create a directory DIR for testing, and copy or link test_data/Wikipedia_small_subset.bz2 as corpus.bz2.

::

 $ ln -s ../malaprop/test/data/Wikipedia_small_subset.bz1 DIR/corpus.bz2

Run 

::

 $ scons data_directory=DIR test=1

You should find small correction and adversarial task output in DIR to examine.

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

* correction_task or adversarial_task
    * DIR must contain development_set.bz2 or dependencies met for learning_sets
    * lines_per_chunk=n (defaults to 100000)
    * error_rate e in {0,1} (defaults to .05)
    * vocabulary_size=n
    * DIR must contain nK.real_word_vocab 
      OR 
    * dependencies met for real_word_vocabulary_files

    * correction task:
      * -> corrupted_error_rate_e_nK_vocabulary.bz2
      * -> corrections_error_rate_e_nK_vocabulary.bz2
    * adversarial task:
      * -> adversarial_error_rate_e_nK_vocabulary.bz2
      * -> key_error_rate_e_nK_vocabulary.bz2

Note: vocabulary_size is given in thousands.

================
Acknowledgements
================
Zooko Wilcox-O'Hearn contributed endless hours to engineering and debuggery advice.

.. _the adversarial evaluation paradigm for natural language processing proposed by Noah Smith: http://arxiv.org/abs/1207.0245

.. _Damerau-Levenshtein: http://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance

.. _recluse: https://github.com/lamber/recluse
