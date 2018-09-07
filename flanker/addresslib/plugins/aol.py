# coding:utf-8

'''
    Email address validation plugin for aol.com email addresses.

    Notes:

        3-32 characters
        must start with letter
        must end with letter or number
        must use letters, numbers, dot (.) or underscores (_)
        no consecutive dot (.) or underscores (_)
        no dot-underscore (._) or underscore-dot (_.)
        case is ignored

    Grammar:

        local-part  ->  alpha { [ dot | underscore ] ( alpha | num ) }

'''
import re
from flanker.addresslib.plugins._tokenizer import TokenStream
from flanker.addresslib._parser.lexer import _UNICODE_CHAR

ALPHA      = re.compile(r'''
                        ( [A-Za-z]
                        | {unicode_char}
                        )+
                        '''.format(unicode_char=_UNICODE_CHAR),
                        re.MULTILINE | re.VERBOSE)

NUMERIC    = re.compile(r'''
                        ( [0-9]
                        )+
                        ''',
                        re.MULTILINE | re.VERBOSE)

ALPHANUM   = re.compile(r'''
                        ( [A-Za-z0-9]
                        | {unicode_char}
                        )+
                        '''.format(unicode_char=_UNICODE_CHAR),
                        re.MULTILINE | re.VERBOSE)

DOT        = '.'
UNDERSCORE = '_'

AOL_UNMANAGED = ['verizon.net']


def validate(email_addr):
    # Setup for handling EmailAddress type instead of literal string
    localpart = email_addr.mailbox
    unmanaged = unmanaged_email(email_addr.hostname)

    # check string exists and not empty
    if not localpart:
        return False

    # Unmanaged is now a list of providers whom patterns/rules are unknown
    # thus any hostname part matching will return without rule adherence.
    if unmanaged:
        return True

    # length check
    l = len(localpart)
    if l < 3 or l > 32:
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


def unmanaged_email(hostname):
    return hostname in AOL_UNMANAGED
