# coding:utf-8

'''
    Email address validation plugin for yahoo.com email addresses.

    Notes for primary e-mail:

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

    Notes for disposable e-mails using "AddressGuard":

        example: base-keyword@yahoo.com

        base and keyword may each be up to 32 characters
        base may contain letters, numbers, underscores
        base must start with a letter
        keyword may contain letters and numbers
        a single hyphen (-) connects the base and keyword

    Grammar:

        local-part  ->  alpha { [ alpha | num | underscore ] } hyphen { [ alpha | num ] }

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

HYPHEN     = re.compile(r'''
                        \-
                        ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    # must start with letter
    if len(localpart) < 1 or ALPHA.match(localpart[0]) is None:
        return False

    # must end with letter or digit
    if ALPHANUM.match(localpart[-1]) is None:
        return False

    # only disposable addresses may contain hyphens
    if HYPHEN.search(localpart):
        return _validate_disposable(localpart)

    # otherwise, normal validation
    return _validate_primary(localpart)


def _validate_primary(localpart):
    # length check
    l = len(localpart)
    if l < 4 or l > 32:
        return False

    # no more than one dot (.)
    if localpart.count('.') > 1:
        return False

    # Grammar: local-part -> alpha  { [ dot | underscore ] ( alpha | num ) }"
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

def _validate_disposable(localpart):
    # length check (base + hyphen + keyword)
    l = len(localpart)
    if l < 3 or l > 65:
        return False

    # single hyphen
    if localpart.count('-') != 1:
        return False

    # base and keyword length limit
    parts = localpart.split('-')
    for part in parts:
        l = len(part)
        if l < 1 or l > 32:
            return False

    # Grammar: local-part  ->  alpha { [ alpha | num | underscore ] } hyphen { [ alpha | num ] }
    stream = TokenStream(localpart)

    # must being with alpha
    begin = stream.get_token(ALPHA)
    if begin is None:
        return False

    while True:
        # alpha, num, underscore
        base = stream.get_token(ALPHANUM) or stream.get_token(UNDERSCORE)

        if base is None:
            break

    # hyphen
    hyphen = stream.get_token(HYPHEN)
    if hyphen is None:
        return False

    # keyword must be alpha, num
    stream.get_token(ALPHANUM)

    if not stream.end_of_stream():
        return False

    return True
