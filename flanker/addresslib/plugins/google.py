# coding:utf-8

'''
    Email address validation plugin for Google Apps email addresses.

    Notes:

        must be between 1-64 characters
        must use letters, numbers, dash (-), underscore (_), apostrophes ('), and dots (.)
        if one character, must be alphanum, underscore (_) or apostrophes (')
        otherwise must start with: alphanum, underscore (_), dash (-), or apostrophes(')
        otherwise must end with: alphanum, underscore(_), dash(-), or apostrophes(')
        plus (+) is allowed, everything after + is ignored
        case is ignored

    Grammar:

        local-part      ->      main-part [ tags ]
        main-part       ->      google-prefix google-root google-suffix
        tags            ->      { + [ atom ] }
        google-prefix    ->     alphanum | underscore | dash | apostrophe
        google-root      ->     alphanum | underscore | dash | apostrophe | dots
        google-suffix    ->     alphanum | underscore | dash | apostrophe

    Other limitations:

        1. All characters prefixing the plus symbol (+) must be between 1-64 characters.

'''
import re
from flanker.addresslib.plugins._tokenizer import TokenStream
from flanker.addresslib._parser.lexer import t_ATOM, _UNICODE_CHAR

ATOM        = re.compile(t_ATOM, re.MULTILINE | re.VERBOSE)

GOOGLE_BASE = re.compile(r'''
                         ( [A-Za-z0-9_\-'\.]
                         | {unicode_char}
                         )+
                         '''.format(unicode_char=_UNICODE_CHAR),
                         re.MULTILINE | re.VERBOSE)

ALPHANUM    = re.compile(r'''
                         ( [A-Za-z0-9]
                         | {unicode_char}
                         )+
                         '''.format(unicode_char=_UNICODE_CHAR),
                         re.MULTILINE | re.VERBOSE)

APOSTROPHE  = re.compile(r'''
                         \'
                         ''',
                         re.MULTILINE | re.VERBOSE)

UNDERSCORE  = re.compile(r'\_', re.MULTILINE | re.VERBOSE)
DASH        = re.compile(r'\-', re.MULTILINE | re.VERBOSE)

DOTS        = '.'
PLUS        = '+'


def validate(email_addr):
    # Setup for handling EmailAddress type instead of literal string
    localpart = email_addr.mailbox

    # check string exists and not empty
    if not localpart:
        return False

    lparts = localpart.split('+')
    real_localpart = lparts[0]

    # length check
    l = len(real_localpart)
    if l < 0 or l > 64:
        return False

    # if only one character, must be alphanum, underscore (_), or apostrophe (')
    if len(localpart) == 1 or l == 1:
        if ALPHANUM.match(localpart) or UNDERSCORE.match(localpart) or \
            APOSTROPHE.match(localpart):
            return True
        return False

    # must start with: alphanum, underscore (_), dash (-), or apostrophe(')
    if len(real_localpart) > 0:
        if not ALPHANUM.match(real_localpart[0]) and not UNDERSCORE.match(real_localpart[0]) \
            and not DASH.match(real_localpart[0]) and not APOSTROPHE.match(real_localpart[0]):
            return False
    else:
        return False

    # must end with: alphanum, underscore(_), dash(-), or apostrophe(')
    if not ALPHANUM.match(real_localpart[-1]) and not UNDERSCORE.match(real_localpart[-1]) \
        and not DASH.match(real_localpart[-1]) and not APOSTROPHE.match(real_localpart[-1]):
        return False

    # grammar check
    return _validate(real_localpart)

def _validate(localpart):
    stream = TokenStream(localpart)

    # get the google base
    mpart = stream.get_token(GOOGLE_BASE)
    if mpart is None:
        return False

    # optional tags
    tgs = _tags(stream)

    if not stream.end_of_stream():
        return False

    return True


def _tags(stream):
    while True:
        # plus sign
        pls = stream.get_token(PLUS)

        # optional atom
        if pls:
            stream.get_token(ATOM)
        else:
            break

    return True
