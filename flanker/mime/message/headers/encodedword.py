# coding:utf-8
import logging
import regex as re

import email.quoprimime
import email.base64mime

from base64 import b64encode

from flanker.mime.message import charsets, errors

log = logging.getLogger(__name__)

#deal with unfolding
foldingWhiteSpace = re.compile(r"(\n\r?|\r\n?)(\s*)")


def unfold(value):
    """
    Unfolding is accomplished by simply removing any CRLF
    that is immediately followed by WSP.  Each header field should be
    treated in its unfolded form for further syntactic and semantic
    evaluation.
    """
    return re.sub(foldingWhiteSpace, r"\2", value)


def decode(header, mimepart_charset=None):
    return mime_to_unicode(header, mimepart_charset)


def mime_to_unicode(header, mimepart_charset=None):
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
    if not isinstance(header, basestring):
        return header

    try:
        header = unfold(header)
        decoded = []  # decoded parts

        acc_str = ''
        acc_str_charset = None
        acc_str_encoding = None
        while header:
            match = encodedWord.search(header)
            if match:
                start = match.start()
                if start != 0:
                    # decodes unencoded ascii part to unicode
                    value = charsets.convert_to_unicode(ascii, header[0:start])
                    if value.strip():
                        if acc_str:
                            raise errors.DecodingDataCorruptionError()

                        decoded.append(value)

                # decode a header =?...?= of encoding
                if (acc_str_charset is not None and acc_str_charset != match.group('charset').lower()) or \
                    (acc_str_encoding is not None and acc_str_encoding != match.group('encoding').lower()):
                        raise errors.DecodingDataCorruptionError()
                charset, value = decode_part(
                    match.group('charset').lower() if match.group('charset') else mimepart_charset,
                    match.group('encoding').lower(),
                    acc_str+match.group('encoded') if len(acc_str) > 0 else match.group('encoded'))
                try:
                    decode_str = charsets.convert_to_unicode(charset, value)
                except errors.DecodingDataCorruptionError as e:
                    acc_str += match.group('encoded')
                    acc_str_charset = match.group('charset').lower()
                    acc_str_encoding = match.group('encoding').lower()
                    header = header[match.end():]
                    continue

                acc_str = ''
                acc_str_charset = None
                acc_str_encoding = None
                decoded.append(decode_str)
                header = header[match.end():]
            else:
                # no match? append the remainder
                # of the string to the list of chunks
                if acc_str:
                    raise errors.DecodingDataCorruptionError()
                decoded.append(charsets.convert_to_unicode(ascii, header))
                break

        if acc_str:
            raise errors.DecodingDataCorruptionError()

        return u"".join(decoded)
    except Exception:
        try:
            logged_header = header
            if isinstance(logged_header, unicode):
                logged_header = logged_header.encode('utf-8')
                # encode header as utf-8 so all characters can be base64 encoded
            logged_header = b64encode(logged_header)
            log.warning(
                u"HEADER-DECODE-FAIL: ({0}) - b64encoded".format(
                    logged_header))
        except Exception:
            log.exception("Failed to log exception")
        return header

def decode_acc_str(acc_str, acc_charset, encoding):
    charset, value = decode_part(acc_charset, encoding, acc_str)
    acc_str = ''
    acc_charset = None
    encoding = None
    return charsets.convert_to_unicode(charset, value)

ascii = 'ascii'

#this spec refers to
#http://tools.ietf.org/html/rfc2047
encodedWord = re.compile(r'''(?P<encodedWord>
  =\?                  # literal =?
  (?P<charset>[^?]*?)  # non-greedy up to the next ? is the charset
  \?                   # literal ?
  (?P<encoding>[qb])   # either a "q" or a "b", case insensitive
  \?                   # literal ?
  (?P<encoded>.*?)     # non-greedy up to the next ?= is the encoded string
  \?=                  # literal ?=
)''', re.VERBOSE | re.IGNORECASE | re.MULTILINE)


def decode_part(charset, encoding, value):
    """
    Attempts to decode part, understands
    'q' - quoted encoding
    'b' - base64 mime encoding

    Returns (charset, decoded-string)
    """
    if encoding == 'q':
        return (charset, email.quoprimime.header_decode(str(value)))

    elif encoding == 'b':
        # Postel's law: add missing padding
        paderr = len(value) % 4
        if paderr:
            value += '==='[:4 - paderr]
        return (charset, email.base64mime.decode(value))

    elif not encoding:
        return (charset, value)

    else:
        raise errors.DecodingError(
            "Unknown encoding: {0}".format(encoding))
