Malaprop
Author: L. Amber Wilcox-O'Hearn
Date: February 5th, 2013

===
Introduction
===
Malaprop is a project involving transformations of natural text that result in some words being replaced by near neighbours.  From Wikipedia: Mrs. Malaprop is a character "in Richard Brinsley Sheridan's 1775 play The Rivals who frequently misspeaks (to great comic effect) by using words which don't have the meaning she intends, but which sound similar to words that do."  Graeme Hirst and Alex Budanitsky first used the term malapropism in the context of this computational task.

Malaprop is written in the spirit of the adversarial evaluation paradigm for natural language processing introduced by Noah Smith.  Please see http://subsymbol.org for discussion.

This first version includes code to 
(1) Divide a corpus of Wikipedia articles into training, development, and test sets.
(2) Generate trigram models from a training set.
(3) Create a corpus of real-word errors embedded in development and test sets:

It acts as a noisy channel, randomly inserting Damerau-Levenshtein ( http://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance ) errors at the character level as a word is passed through. If the resulting string is a *real word* — that is, a sufficiently frequent word in the original corpus — the new word replaces the original.

===
Dependencies
===
Malaprop was tested using the following software:

Ubuntu 12.04.2 LTS
Python 2.7.3
SCons v2.1.0.r5357
NLTK 2.0b9
SRILM 1.5.5

===
Running the tests
===
===
Running Malaprop
===

===
Ackowledgements
===
This project would never have survived without the endless personal support and technical advice from my husband, Zooko Wilcox-O'Hearn, and the enduring faith and loyalty of my graduate advisor, Graeme Hirst.
