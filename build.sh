#!/bin/bash

# Make sure the script fails fast.
set -e
set -u

if [[ ${TRAVIS_PYTHON_VERSION} == 2.7* ]]; then
    nosetests --with-coverage --cover-package=flanker
else
    nosetests --with-coverage --cover-package=flanker tests/mime/bounce_tests.py
fi
