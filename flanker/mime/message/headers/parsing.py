import string
import regex
from collections import deque
from flanker.mime.message.headers import encodedword, parametrized
from flanker.mime.message.headers.wrappers import ContentType, WithParams
from flanker.mime.message.errors import DecodingError
from flanker.mime.message.utils import to_unicode
from flanker.utils import is_pure_ascii

_RE_HEADER = regex.compile(r'^(From |[\041-\071\073-\176]+:|[\t ])')


def normalize(header_name):
    return string.capwords(header_name.lower(), '-')


def parse_stream(stream):
    """Reads the incoming stream and returns list of tuples"""
    out = deque()
    for header in _unfold_header_lines(_read_header_lines(stream)):
        out.append(parse_header(header))

    return out


def parse_header(header):
    """ Accepts a raw header with name, colons and newlines
    and returns it's parsed value
    """
    name, val = _split_header(header)
    if not is_pure_ascii(name):
        raise DecodingError('Non-ascii header name')

    return name, parse_header_value(name, encodedword.unfold(val))


def parse_header_value(name, val):
    if not is_pure_ascii(val):
        val = to_unicode(val)
    if parametrized.is_parametrized(name, val):
        val, params = parametrized.decode(val)
        if val is not None and not is_pure_ascii(val):
            raise DecodingError('Non-ascii content header value')
        if name == 'Content-Type':
            main, sub = parametrized.fix_content_type(val)
            return ContentType(main, sub, params)

        return WithParams(val, params)

    return val


def is_empty(line):
    return line in ('\r\n', '\r', '\n')


def _read_header_lines(fp):
    """Read lines with headers until the start of body"""
    lines = deque()
    for line in fp:
        if is_empty(line):
            break

        # tricky case if it's not a header and not an empty line
        # ususally means that user forgot to separate the body and newlines
        # so "unread" this line here, what means to treat it like a body
        if not _RE_HEADER.match(line):
            fp.seek(fp.tell() - len(line))
            break

        lines.append(line)

    return lines


def _unfold_header_lines(lines):
    headers = deque()
    for line in lines:
        # ignore unix from
        if line.startswith('From '):
            continue

        # this is continuation
        if line[0] in ' \t':
            _extend_last_header(headers, line)
            continue

        headers.append(line)

    new_headers = deque()
    for h in headers:
        if isinstance(h, deque):
            new_headers.append(''.join(h).rstrip('\r\n'))
            continue

        new_headers.append(h.rstrip('\r\n'))

    return new_headers


def _extend_last_header(headers, line):
    # Ignore continuation header lines at the top of a part.
    if len(headers) == 0:
        return

    header = headers.pop()

    # If the latest header is already multiline then extend it.
    if isinstance(header, deque):
        header.append(line)
        headers.append(header)
        return

    # Convert the latest header to a multiline one.
    headers.append(deque((header, line)))


def _split_header(header):
    pair = header.split(':', 1)
    if len(pair) == 2:
        return normalize(pair[0].rstrip()), pair[1].lstrip()

    return None, None
