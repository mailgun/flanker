# coding:utf-8

import sys
from setuptools import setup, find_packages


setup(name='flanker',
      version='0.4.30',
      description='Mailgun Parsing Tools',
      long_description=open('README.rst').read(),
      classifiers=[],
      keywords='',
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='http://mailgun.net',
      license='Apache 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      tests_require=[
          'nose',
          'mock'
      ],
      install_requires=[
          'chardet',
          'cchardet',
          'cython',
          'dnsq',
          'expiringdict',
          'WebOb',
          'redis',
          # IMPORTANT! Newer regex versions are a lot slower for
          # mime parsing (100x slower) so keep it as-is for now.
          'regex>=0.1.20110315',
      ],
      )
