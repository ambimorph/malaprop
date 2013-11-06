=========
MALAPROP
=========
Release 0.4.0 (2013-11-06)
..........................
* Now uses recluses article_selector to get a much smaller subset of the original corpus, and store an index to those articles.
* Implements a trigram-based chooser for the adversarial task.
* Includes data sets for replication.

Release 0.3.0 (2013-10-28)
..........................
* Added a new channel model to use confusion sets instead of operating by character.
* SCons now uses DamerauLevenshteinDerivor to generate confusion sets for the error set creation.

Release 0.2.0 (2013-10-23)
..........................
* Refactored the channel model, and changed its interface.
* Added the adversarial task as a possible target.
* Removed multiple vocabulary sizes in a single call to SCons.

Release 0.1.0 (2013-10-04)
..........................
* This version of malaprop relies on recluse for experimental set up and some of the model building.
* It also uses `versioneer`_ for version management.

.. _versioneer: https://github.com/warner/python-versioneer
