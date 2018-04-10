# coding:utf-8
import logging
from base64 import b64encode

import regex as re
import six

from flanker import _email
from flanker.mime.message import charsets, errors

_log = logging.getLogger(__name__)

_RE_FOLDING_WHITE_SPACES = re.compile(r"(\n\r?|\r\n?)(\s*)")

# This spec refers to http://tools.ietf.org/html/rfc2047
_RE_ENCODED_WORD = re.compile(r'''(?P<encodedWord>
  =\?                  # literal =?
  (?P<charset>[^?]*?)  # non-greedy up to the next ? is the charset
  \?                   # literal ?
  (?P<encoding>[qb])   # either a "q" or a "b", case insensitive
  \?                   # literal ?
  (?P<encoded>.*?)     # non-greedy up to the next ?= is the encoded string
  \?=                  # literal ?=
)''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)


def unfold(value):
    """
    Unfolding is accomplished by simply removing any CRLF
    that is immediately followed by WSP.  Each header field should be
    treated in its unfolded form for further syntactic and semantic
    evaluation.
    """
    return re.sub(_RE_FOLDING_WHITE_SPACES, r'\2', value)


def decode(header):
    return mime_to_unicode(header)


def mime_to_unicode(header):
    """
    Takes a header value and returns a fully decoded unicode string.
    It differs from standard Python's mail.header.decode_header() because:
        - it is higher level, i.e. returns a unicode string instead of
          an array of tuples
        - it accepts Unicode and non-ASCII strings as well

    >>> header_to_unicode("=?UTF-8?B?UmVbMl06INCX0LXQvNC70Y/QutC4?=")
        u"Земляки"
    >>> header_to_unicode("hello")
        u"Hello"
    """
    # Only string header values need to be converted.
    if not isinstance(header, six.string_types):
        return header

    try:
        header = unfold(header)
        decoded = []  # decoded parts

        while header:
            match = _RE_ENCODED_WORD.search(header)
            if not match:
                # Append the remainder of the string to the list of chunks.
                decoded.append(charsets.convert_to_unicode('ascii', header))
                break

            start = match.start()
            if start != 0:
                # decodes unencoded ascii part to unicode
                value = charsets.convert_to_unicode('ascii', header[0:start])
                if value.strip():
                    decoded.append(value)
            # decode a header =?...?= of encoding
            charset, value = _decode_part(match.group('charset').lower(),
                                          match.group('encoding').lower(),
                                          match.group('encoded'))
            decoded.append(charsets.convert_to_unicode(charset, value))
            header = header[match.end():]

        return u"".join(decoded)
    except Exception:
        try:
            logged_header = header
            if isinstance(logged_header, six.text_type):
                logged_header = logged_header.encode('utf-8')
                # encode header as utf-8 so all characters can be base64 encoded
            logged_header = b64encode(logged_header)
            _log.warning(
                u"HEADER-DECODE-FAIL: ({0}) - b64encoded".format(
                    logged_header))
        except Exception:
            _log.exception("Failed to log exception")
        return header


def _decode_part(charset, encoding, value):
    """
    Attempts to decode part, understands
    'q' - quoted encoding
    'b' - base64 mime encoding

    Returns (charset, decoded-string)
    """
    if encoding == 'q':
        return charset, _decode_quoted_printable(value)

    if encoding == 'b':
        # Postel's law: add missing padding
        paderr = len(value) % 4
        if paderr:
            value += '==='[:4 - paderr]

        return charset, _email.decode_base64(value)

    if not encoding:
        return charset, value

    raise errors.DecodingError('Unknown encoding: %s' % encoding)


def _decode_quoted_printable(qp):
    if six.PY2:
        return _email.decode_quoted_printable(str(qp))

    buf = bytearray()
    size = len(qp)
    i = 0
    while i < size:
        ch = qp[i]
        i += 1
        if ch == '_':
            buf.append(ord(' '))
            continue

        if ch != '=':
            buf.append(ord(ch))
            continue

        # If there is no enough characters left, then treat them as is.
        if size - i < 2:
            buf.append(ord(ch))
            continue

        try:
            codepoint = int(qp[i:i + 2], 16)
        except ValueError:
            buf.append(ord(ch))
            continue

        buf.append(codepoint)
        i += 2

    return six.binary_type(buf)
