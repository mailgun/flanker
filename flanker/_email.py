import email
from contextlib import closing
from email.generator import Generator
from email.header import Header
from email.mime import audio
from email.utils import make_msgid

import six
from six.moves import StringIO

_CRLF = '\r\n'
_SPLIT_CHARS = ' ;,'

# The value of email.header.MAXLINELEN constant changed from 76 to 78 in
# Python 3. To make sure that the library behaviour is consistent across all
# Python versions we introduced our own constant.
_MAX_LINE_LEN = 76


if six.PY3:
    from email.policy import Compat32

    class _Compat32CRLF(Compat32):
        linesep = _CRLF

    _compat32_crlf = _Compat32CRLF()

else:
    from email import generator, header, quoprimime, feedparser
    generator.NL = _CRLF
    header.NL = _CRLF
    quoprimime.NL = _CRLF
    feedparser.NL = _CRLF


def message_from_string(string):
    if six.PY3:
        if isinstance(string, six.binary_type):
            return email.message_from_bytes(string, policy=_compat32_crlf)

        return email.message_from_string(string, policy=_compat32_crlf)

    return email.message_from_string(string)


def message_to_string(msg):
    """
    Converts python message to string in a proper way.
    """
    with closing(StringIO()) as fp:
        if six.PY3:
            g = Generator(fp, mangle_from_=False, policy=_compat32_crlf)
            g.flatten(msg, unixfrom=False)
            return fp.getvalue()

        g = Generator(fp, mangle_from_=False)
        g.flatten(msg, unixfrom=False)

        # In Python 2 Generator.flatten uses `print >> ` to write to fp, that
        # adds `\n` regardless of generator.NL value. So we resort to a hackish
        # way of replacing LF with RFC complaint CRLF.
        for i, v in enumerate(fp.buflist):
            if v == '\n':
                fp.buflist[i] = _CRLF

        return fp.getvalue()


def format_param(name, val):
    return email.message._formatparam(name, val)


def decode_base64(val):
    return email.base64mime.decode(val)


def encode_base64(val):
    return email.encoders._bencode(val)


def decode_quoted_printable(val):
    return email.quoprimime.header_decode(val)


def detect_audio_type(val):
    return audio._whatsnd(val)


def make_message_id():
    return make_msgid()


def encode_header(name, val, encoding='ascii', max_line_len=_MAX_LINE_LEN):
    header = Header(val, encoding, max_line_len, name)
    if six.PY3:
        return header.encode(_SPLIT_CHARS, linesep=_CRLF)

    return header.encode(_SPLIT_CHARS)
