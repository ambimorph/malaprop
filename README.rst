Malaprop
Author: L. Amber Wilcox-O'Hearn
Date: March 3rd, 2013

============
Introduction
============
Malaprop is a project involving transformations of natural text that result in some words being replaced by real-word near neighbours.  From Wikipedia: Mrs. Malaprop is a character "in Richard Brinsley Sheridan's 1775 play The Rivals who frequently misspeaks (to great comic effect) by using words which don't have the meaning she intends, but which sound similar to words that do."   The term malapropism was first used in the context of this computational task by Graeme Hirst and Alex Budanitsky.

Malaprop is written in the spirit of the adversarial evaluation paradigm for natural language processing proposed by Noah Smith.  Please see http://subsymbol.org for discussion.

This first version includes code to 
(1) Divide a corpus of Wikipedia articles into training, development, and test sets.
(2) Generate trigram models from a training set.
(3) Create a corpus of real-word errors embedded in the development set:

It acts as a noisy channel, randomly inserting Damerau-Levenshtein ( http://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance ) errors at the character level as a word is passed through. If the resulting string is a *real word* — that is, a sufficiently frequent word in the original corpus — the new word replaces the original.

============
Dependencies
============
Malaprop was tested using the following software:

Ubuntu 12.04.2 LTS
Python 2.7.3
SCons v2.1.0.r5357
NLTK 2.0b9
SRILM 1.5.5

=================
Running the tests
=================
Unit tests: Run $ python -m unittest discover

SCons test
Create a directory DIR for testing, and copy or link your b2zipped corpus as corpus.bz2.
Run $ scons data_directory=DIR test=1

=================================
Running Malaprop on your own data
=================================
Create a directory DIR for testing, and copy or link your b2zipped corpus as corpus.bz2.
Run $ scons data_directory=DIR variables target

Possible targets at this point are: learning_sets, vocabulary_files, trigram_models, real_word_vocabulary_files, and error_sets.

In addition to the presence of the corpus.bz2 file, targets require these variables:

* learning_sets (requires no further arguments)
* vocabulary_files, trigram_models:
    * one or more variables vocabulary_size=n
    * lines_per_chunk=n (defaults to 100000)
* real_word_vocabulary_files
    * one or more variables vocabulary_size=n
    * lines_per_chunk=n (defaults to 100000) (only needed if vocabulary_files not already built)
* error_sets
    * one or more variables vocabulary_size=n
    * lines_per_chunk=n (defaults to 100000)
    * error_rate in {0,1} (defaults to .05)

Note: vocabulary_size is given in thousands.

================
Acknowledgements
================
Zooko Wilcox-O'Hearn contributed endless hours to engineering and debuggery advice.
