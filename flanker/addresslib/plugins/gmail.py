# coding:utf-8

'''
    Email address validation plugin for gmail.com email addresses.

    Notes:

        must be between 6-30 characters
        must start with letter or number
        must end with letter or number
        must use letters, numbers, or dots (.)
        all dots (.) are ignored
        case is ignored
        plus (+) is allowed, everything after + is ignored
      1. All characters prefixing the plus symbol (+) and stripping all dot
           symbol (.) must be between 6-30 characters.


    Grammar:

        local-part      ->      main-part [ tags ]
        main-part       ->      gmail-prefix gmail-root gmail-suffix
        tags            ->      { + [ gmail-root ] }
        gmail-prefix    ->      alpha | num
        gmail-root      ->      alpha | num | dot
        gmail-suffix    ->      alpha | num
'''
import re
from flanker.addresslib.tokenizer import TokenStream
from flanker.addresslib.tokenizer import ATOM


GMAIL_BASE = re.compile(r'''
                        [A-Za-z0-9\.]+
                        ''', re.MULTILINE | re.VERBOSE)

ALPHANUM   = re.compile(r'''
                        [A-Za-z0-9]+
                        ''', re.MULTILINE | re.VERBOSE)

PLUS       = re.compile(r'''
                        [\+]+
                        ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    slpart = localpart.replace('.', '')
    lparts = slpart.split('+')
    real_localpart = lparts[0]

    # length check
    l = len(real_localpart)
    if l < 6 or l > 30:
        return False

   # must start with letter or num
    if ALPHANUM.match(real_localpart[0]) is None:
        return False

    # must end with letter or num
    if ALPHANUM.match(real_localpart[-1]) is None:
        return False

    # grammar check
    return _validate(real_localpart)


def _validate(localpart):
    stream = TokenStream(localpart)

    # get the gmail base (alpha, num, or dot)
    mpart = stream.get_token(GMAIL_BASE)
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
