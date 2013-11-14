import string
import regex
from collections import deque
from flanker.mime.message.headers import encodedword, parametrized
from flanker.mime.message.headers.wrappers import ContentType, WithParams
from flanker.mime.message.errors import DecodingError
from flanker.utils import is_pure_ascii

MAX_LINE_LENGTH = 10000


def normalize(header):
    return string.capwords(header.lower(), '-')


def parse_stream(stream):
    """Reads the incoming stream and returns list of tuples"""
    out = deque()
    for header in unfold(split(stream)):
        out.append(parse_header(header))
    return out

def parse_header(header):
    """ Accepts a raw header with name, colons and newlines
    and returns it's parsed value
    """
    name, val = split2(header)
    if not is_pure_ascii(name):
        raise DecodingError("Non-ascii header name")
    return name, parse_header_value(name, encodedword.unfold(val))

def parse_header_value(name, val):
    if not is_pure_ascii(val):
        if parametrized.is_parametrized(name, val):
            raise DecodingError("Unsupported value in content- header")
        return to_unicode(val)
    else:
        if parametrized.is_parametrized(name, val):
            val, params = parametrized.decode(val)
            if name == 'Content-Type':
                main, sub = parametrized.fix_content_type(val)
                return ContentType(main, sub, params)
            else:
                return WithParams(val, params)
        elif "=?" in val:
            # may be encoded word
            return encodedword.decode(val)
        else:
            return val

def is_empty(line):
    return line in ('\r\n', '\r', '\n')


RE_HEADER = regex.compile(r'^(From |[\041-\071\073-\176]+:|[\t ])')

def split(fp):
    """Read lines with headers until the start of body"""
    lines = deque()
    for line in fp:
        if len(line) > MAX_LINE_LENGTH:
            raise DecodingError(
                "Line is too long: {}".format(len(line)))

        if is_empty(line):
            break

        # tricky case if it's not a header and not an empty line
        # ususally means that user forgot to separate the body and newlines
        # so "unread" this line here, what means to treat it like a body
        if not RE_HEADER.match(line):
            fp.seek(fp.tell() - len(line))
            break

        lines.append(line)

    return lines


def unfold(lines):
    headers = deque()

    for line in lines:
        # ignore unix from
        if line.startswith("From "):
            continue
        # this is continuation
        elif line[0] in ' \t':
            extend(headers, line)
        else:
            headers.append(line)

    new_headers = deque()
    for h in headers:
        if isinstance(h, deque):
            new_headers.append("".join(h).rstrip("\r\n"))
        else:
            new_headers.append(h.rstrip("\r\n"))

    return new_headers


def extend(headers, line):
    try:
        header = headers.pop()
    except IndexError:
        # this means that we got invalid header
        # ignore it
        return

    if isinstance(header, deque):
        header.append(line)
        headers.append(header)
    else:
        headers.append(deque((header, line)))


def split2(header):
    pair = header.split(":", 1)
    if len(pair) == 2:
        return normalize(pair[0].rstrip()), pair[1].lstrip()
    else:
        return (None, None)


def to_unicode(val):
    if isinstance(val, unicode):
        return val
    else:
        try:
            return unicode(val, 'utf-8', 'strict')
        except UnicodeDecodeError:
            raise DecodingError("Non ascii or utf-8 header value")
