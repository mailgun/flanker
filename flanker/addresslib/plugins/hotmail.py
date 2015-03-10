# coding:utf-8

'''
    Email address validation plugin for hotmail.com email addresses.

    Notes:

        1-64 characters
        must start with letter or number
        must end with letter, number, hyphen (-), or underscore (_)
        must use letters, numbers, periods (.), hypens (-), or underscores (_)
        only one plus (+) is allowed
        case is ignored

    Grammar:

        local-part      ->  main-part [ tags ]
        main-part       ->  hotmail-prefix hotmail-root hotmail-suffix
        hotmail-prefix  ->  alpha | number
        hotmail-root    ->  alpha | number | period | hyphen | underscore
        hotmail-suffix  ->  alpha | number | hyphen | underscore
        tags            ->  + [ hotmail-root ]


    Other limitations:

        1. Only one consecutive period (.) is allowed in the local-part
        2. Length of local-part must be no more than 64 characters, and no
           less than 1 characters.

'''
import re
from flanker.addresslib.tokenizer import TokenStream

HOTMAIL_PREFIX  = re.compile(r'''
                            [A-Za-z0-9]+
                            ''', re.MULTILINE | re.VERBOSE)

HOTMAIL_BASE    = re.compile(r'''
                            [A-Za-z0-9\.\-\_]+
                            ''', re.MULTILINE | re.VERBOSE)

HOTMAIL_SUFFIX  = re.compile(r'''
                            [A-Za-z0-9\-\_]+
                            ''', re.MULTILINE | re.VERBOSE)

PLUS            = re.compile(r'''
                            \+
                            ''', re.MULTILINE | re.VERBOSE)

PERIODS         = re.compile(r'''
                            \.{2,}
                            ''', re.MULTILINE | re.VERBOSE)


def validate(localpart):
    # check string exists and not empty
    if not localpart:
        return False

    # remove tag if it exists
    lparts = localpart.split('+')
    real_localpart = lparts[0]

    # length check
    l = len(real_localpart)
    if l < 1 or l > 64:
        return False

    # start can only be alphanumeric
    if HOTMAIL_PREFIX.match(real_localpart[0]) is None:
        return False

    # can not end with dot
    if HOTMAIL_SUFFIX.match(real_localpart[-1]) is None:
        return False

    # no more than one plus (+)
    if localpart.count('+') > 1:
        return False

    # no consecutive periods (..)
    if PERIODS.search(localpart):
        return False

    # grammar check
    retval = _validate(real_localpart)
    return retval


def _validate(localpart):
    stream = TokenStream(localpart)

    # get the hotmail base
    mpart = stream.get_token(HOTMAIL_BASE)
    if mpart is None:
        return False

    # optional tags
    tgs = _tags(stream)

    if not stream.end_of_stream():
        return False

    return True


def _tags(stream):
    pls = stream.get_token(PLUS)
    bse = stream.get_token(HOTMAIL_BASE)

    if bse and pls is None:
        return False

    return True
