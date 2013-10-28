# coding:utf-8

'''
    Email address validation plugin for yahoo.com email addresses.

    Notes:

        4-32 characters
        must start with letter
        must end with letter or number
        must use letters, numbers, underscores (_)
        only one dot (.) allowed
        no consecutive dot (.) or underscore (_)
        no dot-underscore (._) or underscore-dot (_.)
        case is ignored
        tags not supported

    Grammar:

        local-part  ->  alpha  { [ dot | underscore ] ( alpha | num ) }

    Other limitations:

        1. No more than a single dot (.) is allowed in the local-part
        2. Length of local-part must be no more than 32 characters, and no
           less than 4 characters.

'''

import re
from flanker.addresslib.tokenizer import TokenStream

ALPHA      = re.compile(r'''
                        [A-Za-z]+
                        ''', re.MULTILINE | re.VERBOSE)

NUMERIC    = re.compile(r'''
                        [0-9]+
                        ''', re.MULTILINE | re.VERBOSE)

ALPHANUM   = re.compile(r'''
                        [A-Za-z0-9]+
                        ''', re.MULTILINE | re.VERBOSE)

DOT        = re.compile(r'''
                        \.
                        ''', re.MULTILINE | re.VERBOSE)

UNDERSCORE = re.compile(r'''
                        \_
                        ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    # length check
    l = len(localpart)
    if l < 4 or l > 32:
        return False

    # no more than one dot (.)
    if localpart.count('.') > 1:
        return False

    # must start with letter
    if ALPHA.match(localpart[0]) is None:
        return False

    # must end with letter or digit
    if ALPHANUM.match(localpart[-1]) is None:
        return False

    # grammar check
    return _validate(localpart)


def _validate(localpart):
    "Grammar: local-part -> alpha  { [ dot | underscore ] ( alpha | num ) }"
    stream = TokenStream(localpart)

    # local-part must being with alpha
    alpa = stream.get_token(ALPHA)
    if alpa is None:
        return False

    while True:
        # optional dot or underscore token
        stream.get_token(DOT) or stream.get_token(UNDERSCORE)

        # alpha or numeric
        alpanum = stream.get_token(ALPHA) or stream.get_token(NUMERIC)
        if alpanum is None:
            break

    # alpha or numeric must be end of stream
    if not stream.end_of_stream():
        return False

    return True
