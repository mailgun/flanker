# coding:utf-8

'''
    Email address validation plugin for icloud.com email addresses.

    Notes:

        3-20 characters
        must start with letter
        must end with letter or number
        must use letters, numbers, dot (.) or underscores (_)
        no consecutive dot (.) or underscores (_)
        case is ignored
        any number of plus (+) are allowed if followed by at least one alphanum

    Grammar:

        local-part -> icloud-prefix { [ dot | underscore ] icloud-root }
            icloud-suffix
        icloud-prefix = alpha
        icloud-root = alpha | num | plus
        icloud-suffix = alpha | num

    Other limitations:

        * Length of local-part must be no more than 20 characters, and no
          less than 3 characters.

    Open questions:

        * Are dot-underscore (._) or underscore-dot (_.) allowed?
        * Is name.@icloud.com allowed?

'''
import re
from flanker.addresslib.tokenizer import TokenStream

ALPHA          = re.compile(r'''
                            [A-Za-z]+
                            ''', re.MULTILINE | re.VERBOSE)

ALPHANUM      = re.compile(r'''
                           [A-Za-z0-9]+
                           ''', re.MULTILINE | re.VERBOSE)


ICLOUD_PREFIX = re.compile(r'''
                           [A-Za-z]+
                           ''', re.MULTILINE | re.VERBOSE)

ICLOUD_BASE   = re.compile(r'''
                           [A-Za-z0-9\+]+
                           ''', re.MULTILINE | re.VERBOSE)

DOT           = re.compile(r'''
                           \.
                           ''', re.MULTILINE | re.VERBOSE)

UNDERSCORE    = re.compile(r'''
                           \_
                           ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    lparts = localpart.split('+')
    real_localpart = lparts[0]

    # length check
    l = len(real_localpart)
    if l < 3 or l > 20:
        return False

    # can not end with +
    if localpart[-1] == '+':
        return False

    # must start with letter
    if ALPHA.match(real_localpart[0]) is None:
        return False

    # must end with letter or digit
    if ALPHANUM.match(real_localpart[-1]) is None:
        return False

    # check grammar
    return _validate(real_localpart)


def _validate(localpart):
    stream = TokenStream(localpart)

    # localpart must start with alpha
    alpa = stream.get_token(ICLOUD_PREFIX)
    if alpa is None:
        return False

    while True:
        # optional dot or underscore
        stream.get_token(DOT) or stream.get_token(UNDERSCORE)

        base = stream.get_token(ICLOUD_BASE)
        if base is None:
            break

    if not stream.end_of_stream():
        return False

    return True
