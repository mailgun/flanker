#!/bin/bash

# Make sure the script fails fast.
set -e
set -u

if [[ ${TRAVIS_PYTHON_VERSION} == 2.7* ]]; then
    nosetests --with-coverage --cover-package=flanker
else
    nosetests --with-coverage --cover-package=flanker tests/mime/bounce_tests.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/threading_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/tokenizer_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/headers/encodedword_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/headers/headers_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/headers/parametrized_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/headers/parsing_test.py
    nosetests --with-coverage --cover-package=flanker tests/mime/message/headers/wrappers_test.py
fi
