#!/usr/bin/env python

from distutils.core import setup
import versioneer

versioneer.versionfile_build='malaprop/_version.py'
versioneer.versionfile_source='malaprop/_version.py'
versioneer.tag_prefix = 'malaprop-'
versioneer.parentdir_prefix = 'malaprop-'


setup(name='malaprop',
      description='Tools for NLP evaluation using the adversarial paradigm',
      long_description=open('README.rst').read(),
      author='L. Amber Wilcox-O\'Hearn',
      author_email='amber@cs.toronto.edu',
      url='https://github.com/lamber/malaprop',
      packages=['malaprop', 'malaprop.test'],
      package_data={"malaprop.test": ["data/*"]},
      license='COPYING',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass()
     )
