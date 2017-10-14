from contextlib import closing
from email.generator import Generator

import cchardet
import chardet
import six

from flanker.mime.message import errors


def python_message_to_string(msg):
    """Converts python message to string in a proper way"""
    with closing(six.StringIO()) as fp:
        g = Generator(fp, mangle_from_=False)
        g.flatten(msg, unixfrom=False)
        return fp.getvalue()

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


def _make_unicode(value, charset=None):
    if isinstance(value, six.text_type):
        return value

    charset = charset or "utf-8"
    try:
        value = value.decode(charset, "strict")
    except (UnicodeError, LookupError):
        value = _guess_and_convert(value)

    return value


def to_utf8(value, charset=None):
    '''
    Safely returns a UTF-8 version of a given string
    >>> utils.to_utf8(u'hi')
        'hi'
    '''

    value = _make_unicode(value, charset)

    return value.encode("utf-8", "strict")


def to_unicode(value, charset=None):
    return _make_unicode(value, charset)
