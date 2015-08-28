# coding:utf-8

'''
    Email address validation plugin for gmail.com email addresses.

    Notes:

        must be between 6-30 characters
        must start with letter or number
        must end with letter or number
        must use letters, numbers, or dots (.)
        consecutive dots (..) are not permitted
        dots (.) at the beginning or end are not permitted
        case is ignored
        plus (+) is allowed, everything after + is ignored
      1. All characters prefixing the plus symbol (+) and stripping all dot
           symbol (.) must be between 6-30 characters.


    Grammar:

        local-part       ->      main-part [ tags ]
        main-part        ->      alphanum { [dot] alphanum }
        tags             ->      { + [ dot-atom ] }
        dot-atom    	 ->      atom { [ dot   atom ] }
        atom             ->      { A-Za-z0-9!#$%&'*+\-/=?^_`{|}~ }
        alphanum         ->      alpha | num
        dot              ->      .
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
                        [\+]
                        ''', re.MULTILINE | re.VERBOSE)
DOT        = re.compile(r'''
                        [\.]
                        ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    lparts = localpart.split('+')
    real_localpart = lparts[0]
    stripped_localpart = real_localpart.replace('.', '')

    # length check
    l = len(stripped_localpart)
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

    while True:
        # get alphanumeric portion
        mpart = stream.get_token(ALPHANUM)
        if mpart is None:
            return False
        # get optional dot, must be followed by more alphanumerics
        mpart = stream.get_token(DOT)
        if mpart is None:
            break

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
