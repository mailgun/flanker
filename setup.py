# coding:utf-8

from setuptools import setup, find_packages

setup(name='flanker',
      version='0.8.5',
      description='Mailgun Parsing Tools',
      long_description=open('README.rst').read(),
      classifiers=[],
      keywords='',
      author='Mailgun Inc.',
      author_email='admin@mailgunhq.com',
      url='https://www.mailgun.com/',
      license='Apache 2',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=True,
      tests_require=[
          'nose',
          'mock'
      ],
      install_requires=[
          'attrs',
          'chardet>=1.0.1',
          'cchardet>=0.3.5',
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
      })
