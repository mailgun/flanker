# coding:utf-8

from setuptools import setup, find_packages

tests_require = [
    'coverage',
    'coveralls',
    'mock',
    'nose',
],

setup(name='flanker',
      version='0.9.16',
      description='Mailgun Parsing Tools',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
      ],
      keywords='',
      author='Mailgun Technologies Inc.',
      author_email='admin@mailgunhq.com',
      url='https://www.mailgun.com/',
      license='Apache 2',
      include_package_data=True,
      zip_safe=True,
      tests_require=tests_require,
      install_requires=[
          'attrs',
          'chardet>=1.0.1',
          'cryptography>=0.5',
          'idna>=2.5',
          'ply>=3.10',
          'regex>=0.1.20110315',
          'six',
          'tld',
          'WebOb>=0.9.8'],
      extras_require={
          'validator': [
              'dnsq>=1.1.6',
              'redis>=2.7.1',
          ],
          'cchardet': [
              'cchardet>=0.3.5',
          ],
          'tests': tests_require,
      })
