Malaprop

Author: L. Amber Wilcox-O'Hearn

Contact: amber@cs.toronto.edu

Released under the GNU AFFERO GENERAL PUBLIC LICENSE, see COPYING file for details.

============
Introduction
============
Malaprop is a project involving transformations of natural text that result in some words being replaced by real-word near neighbours.  

Malaprop is written with `the adversarial evaluation paradigm for natural language processing proposed by Noah Smith`_ in mind.  Please see http://www.subsymbol.org/2013/03/malaprop-v010.html for discussion.

The damerau_levenshtein_channel module emulates a noisy channel, randomly inserting `Damerau-Levenshtein`_  errors at the character level as a word is passed through. If the resulting string is a *real word* — that is, a sufficiently frequent word in the original corpus — the new word replaces the original.

The confusion_set_channel module substitutes known words in a text with other known words probabilistically according to a given confusion set function.  For example, when used with `DamerauLevenshteinDerivor`_ it substitutes words that are within one Damerau-Levenshtein edit distance from the original word.



This version includes code to 

(1) Divide a corpus of text articles (e.g. Wikipedia) into training, development, and test sets (from `recluse`_).

(2) Generate trigram models from a training set by wrapping some specific calls to the srilm tool-kit over text segmented and tokenised using a customised version of the NLTK sentence segmenter.

(3) Create a correction task: a corpus of real-word errors embedded in a copy of the development set along with a separate index to the errors and their corrections.

(4) Create an original text recognition task for adversarial evaluation: a set of pairs of sentences, one original, and one corrupted, and a key to identify them.


*Reproducibility* is prioritised, so projects are completely built using SCons.


==============
Example Output
==============

Correction Task:
================

The following examples are taken directly from the regression tests.  You can replicate them by running the SCons test as described below.  They are also included in the directory malaprop/test/data/.

The corrupted file begins with these lines:

---

| Albedo.
| The albedo of an object is a measure of how strongly it reflects light from light sources such as the Sun.
| It is therefore a more specific from of the term reflectivity.
| Albedo is defined as the ratio off total-reflected to incident electromagnetic radiation.
| It is a unitless measure indicative of a surface's or boy's diffuse reflectivity.
| The word is derived form Latin "albedo" "whiteness", in turn from "albus" "white", and was introduced into optics by Johann Heinrich Lambert in his 1760 work "Photometria".
| The range of possible values is from 0 (dark) so 1 (bright).
| The albedo is an important concept ii climatology and astronomy, as well as in computer graphics and computer vision.
| In climatology i is sometimes expressed as a percentage.
| Its value depends on the frequency of radiation considered: unqualified, ii usually refers to some appropriate average across the spectrum of visible light.
| In general, the albedo depends on the direction and directional distribution of incoming radiation.
| Exceptions are Lambertian surfaces, which scatter radiation in all directions in a cosine function, so their albedo does not depend on the incoming distribution.
| In realistic causes, a bidirectional reflectance distribution function (BRDF) is required top characterize the scattering properties of a surface accurately, although albedos re a very useful first approximation.
| Terrestrial albedo.
| Albedos of typical materials in visible light range from up to 0.9 for fresh snow, to about 0.04 or charcoal, one of the darkest substances.

---

with a corresponding correction file starting like this. The numbers index the sentence, token, and *subtoken* positions.  

(The subtoken positions are all '0' in this example, but refer to tokens that are considered separate even though they occur within the same whitespace-bounded string.  For example, if the string "(I'm not sure)" occurred in the text, it would be interpreted as the following three tokens: ["(I'm", "not", "sure)"], and the following subtokens: [["(", "I", "'m"], ["not"], ["sure", ")"]].  This allows subtoken analysis while preserving the original boundaries.  Details in the `recluse`_ package.):

---

| [2, [[6, 0, "from", "form"]]]
| [3, [[6, 0, "off", "of"]]]
| [4, [[10, 0, "boy", "body"]]]
| [5, [[4, 0, "form", "from"]]]
| [6, [[9, 0, "so", "to"]]]
| [7, [[6, 0, "ii", "in"]]]
| [8, [[2, 0, "i", "it"]]]
| [9, [[10, 0, "ii", "it"]]]
| [12, [[2, 0, "causes", "cases"], [11, 0, "top", "to"], [22, 0, "re", "are"]]]
| [14, [[18, 0, "or", "for"]]]

---

The same input and process give the adversarial task file that starts like this:

---

| ["It is therefore a more specific form of the term reflectivity.", "It is therefore a more specific from of the term reflectivity."]
| ["Albedo is defined as the ratio of total-reflected to incident electromagnetic radiation.", "Albedo is defined as the ratio off total-reflected to incident electromagnetic radiation."]
| ["It is a unitless measure indicative of a surface's or body's diffuse reflectivity.", "It is a unitless measure indicative of a surface's or boy's diffuse reflectivity."]
| ["The word is derived form Latin \"albedo\" \"whiteness\", in turn from \"albus\" \"white\", and was introduced into optics by Johann Heinrich Lambert in his 1760 work \"Photometria\".", "The word is derived from Latin \"albedo\" \"whiteness\", in turn from \"albus\" \"white\", and was introduced into optics by Johann Heinrich Lambert in his 1760 work \"Photometria\"."]
| ["The range of possible values is from 0 (dark) so 1 (bright).", "The range of possible values is from 0 (dark) to 1 (bright)."]
| ["The albedo is an important concept ii climatology and astronomy, as well as in computer graphics and computer vision.", "The albedo is an important concept in climatology and astronomy, as well as in computer graphics and computer vision."]
| ["In climatology i is sometimes expressed as a percentage.", "In climatology it is sometimes expressed as a percentage."]
| ["Its value depends on the frequency of radiation considered: unqualified, ii usually refers to some appropriate average across the spectrum of visible light.", "Its value depends on the frequency of radiation considered: unqualified, it usually refers to some appropriate average across the spectrum of visible light."]
| ["In realistic cases, a bidirectional reflectance distribution function (BRDF) is required to characterize the scattering properties of a surface accurately, although albedos are a very useful first approximation.", "In realistic causes, a bidirectional reflectance distribution function (BRDF) is required top characterize the scattering properties of a surface accurately, although albedos re a very useful first approximation."]
| ["Albedos of typical materials in visible light range from up to 0.9 for fresh snow, to about 0.04 for charcoal, one of the darkest substances.", "Albedos of typical materials in visible light range from up to 0.9 for fresh snow, to about 0.04 or charcoal, one of the darkest substances."]

---

with an answer key file that begins like this:

---

0001111100

---


============
Dependencies
============
Malaprop requires:

Python, `recluse`_, SCons, NLTK, `DamerauLevenshteinDerivor`_, and SRILM.

It was tested under the following versions:

* Ubuntu 12.04.3 LTS
* Python 2.7.3
* recluse 0.2.4
* SCons v2.1.0.r5357
* NLTK 2.0b9
* SRILM 1.5.5
* DamerauLevenshteinDerivor 0.0.2

=================
Running the tests
=================
Unit tests: Run 

::

 $ python -m unittest discover

This should find 22 tests.

SCons test:
Create a directory DIR for testing, and copy or link test/data/Wikipedia_small_subset.bz2 as corpus.bz2.

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

* language_models:
    * DIR must contain training_set.bz2 OR dependencies for learning_sets
    * vocabulary_size=n
    * lines_per_chunk=l (defaults to 100000)

    * -> nK.vocab
    * -> trigram_model_nK.arpa

* real_word_vocabulary_files
    * vocabulary_size=n 
    * DIR must contain nK.vocab
      OR
    * dependencies met for language_models

    * -> nK.real_word_vocab for n in vocabulary_size

* correction_task or adversarial_task
    * DIR must contain development_set.bz2 or dependencies met for learning_sets
    * lines_per_chunk=n (defaults to 100000)
    * error_rate=e in {0,1} (defaults to .05)
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

.. _recluse: https://pypi.python.org/pypi/recluse

.. _DamerauLevenshteinDerivor: https://github.com/lamber/DamerauLevenshteinDerivor
