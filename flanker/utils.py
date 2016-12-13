# coding:utf-8
"""
Utility functions and classes used by flanker.
"""
import re

import cchardet
import chardet

from functools import wraps
from flanker.mime.message import errors


def _guess_and_convert(value):
    """
    Try to guess the encoding of the passed value and decode it.

    Uses cchardet to guess the encoding and if guessing or decoding fails, falls
    back to chardet which is much slower.
    """
    try:
        return _guess_and_convert_with(value, detector=cchardet)
    except:
        return _guess_and_convert_with(value, detector=chardet)


def _guess_and_convert_with(value, detector=cchardet):
    """
    Try to guess the encoding of the passed value with the provided detector
    and decode it.

    The detector is either chardet or cchardet module.
    """
    charset = detector.detect(value)

    if not charset["encoding"]:
        raise errors.DecodingError("Failed to guess encoding")

    try:
        value = value.decode(charset["encoding"], "replace")
        return value

    except (UnicodeError, LookupError) as e:
        raise errors.DecodingError(str(e))


def _make_unicode(value, charset=None):
    if isinstance(value, unicode):
        return value

    charset = charset or "utf-8"
    try:
        value = value.decode(charset, "strict")
    except (UnicodeError, LookupError):
        value = _guess_and_convert(value)

    return value


def to_unicode(value, charset=None):
    return _make_unicode(value, charset)


def to_utf8(value, charset=None):
    '''
    Safely returns a UTF-8 version of a given string
    >>> utils.to_utf8(u'hi')
        'hi'
    '''

    value = _make_unicode(value, charset)

    return value.encode("utf-8", "strict")


def is_pure_ascii(value):
    '''
    Determines whether the given string is a pure ascii
    string
    >>> utils.is_pure_ascii(u"Cаша")
        False
    >>> utils.is_pure_ascii(u"Alice")
        True
    >>> utils.is_pure_ascii("Alice")
        True
    '''

    if value is None:
        return False
    if not isinstance(value, basestring):
        return False

    try:
        value.encode("ascii")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
    return True


def cleanup_display_name(name):
    return name.strip(''';,'\r\n ''')


def cleanup_email(email):
    return email.strip("<>;, ")


def contains_control_chars(s):
    if CONTROL_CHAR_RE.match(s):
        return True
    return False


def metrics_wrapper():

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return_value = f(*args, **kwargs)
            if 'metrics' in kwargs and kwargs['metrics'] == True:
                #return all values
                return return_value

            # if we have a single item
            if len(return_value[:-1]) == 1:
                return return_value[0]

            # return all except the last value
            return return_value[:-1]

        return wrapper

    return decorate


# allows, \t\n\v\f\r (0x09-0x0d)
CONTROL_CHARS = ''.join(map(unichr, range(0, 9) + range(14, 32) + range(127, 160)))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(CONTROL_CHARS))
