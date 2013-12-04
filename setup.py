"""Flanker Package Setup"""

from setuptools import setup, find_packages

setup(name='flanker',
      version='0.3.3',
      description='Mailgun Parsing Tools',
      long_description='',
      classifiers=[],
      keywords='',
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='http://mailgun.net',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'chardet>=1.0.1',
        'dnsq>=1.0',
        'expiringdict>=1.0',
        'Paste>=1.7.5',
        'redis>=2.7.1',
         # IMPORTANT! Newer regex versions are a lot slower for
         # mime parsing (100x slower) so keep it as-is for now.
         'regex==0.1.20110315',
      ],
      tests_require=[
        'mock>=1.0.1',
        'nose>=1.2.1',
      ],
      test_suite = 'nose.collector'
)
