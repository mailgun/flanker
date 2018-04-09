#!/bin/bash

# Make sure the script fails fast.
set -e
set -u

if [[ ${TRAVIS_PYTHON_VERSION} == 2.7* ]]; then
    nosetests --with-coverage --cover-package=flanker
else
    nosetests --with-coverage --cover-package=flanker \
        tests/addresslib \
        tests/mime/bounce_tests.py \
        tests/mime/message/headers \
        tests/mime/message/threading_test.py \
        tests/mime/message/tokenizer_test.py \
        tests/mime/message/headers/encodedword_test.py \
        tests/mime/message/headers/headers_test.py \
        tests/mime/message/headers/parametrized_test.py \
        tests/mime/message/headers/parsing_test.py \
        tests/mime/message/headers/wrappers_test.py
fi
