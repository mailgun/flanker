"""Module that is responsible for parsing parameterized header values
encoded in accordance to rfc2231 (new style) or rfc1342 (old style)
"""
import urllib
import regex as re
from flanker.mime.message.headers import encodedword
from flanker.mime.message import charsets
from collections import deque
from itertools import groupby


def decode(header):
    """Accepts parameterized header value (encoded in accordance to
     rfc2231 (new style) or rfc1342 (old style)
     and returns tuple:
         value, {'key': u'val'}
     returns None in case of any failure
    """
    value, rest = split(encodedword.unfold(header))
    if value is None:
        return None, {}
    elif value:
        return value, decode_parameters(rest)


def is_parametrized(name, value):
    return name in ("Content-Type", "Content-Disposition",
                    "Content-Transfer-Encoding")


def fix_content_type(value, default=None):
    """Content-Type value may be badly broken"""
    if not value:
        return default or ('text', 'plain')
    values = value.lower().split("/")
    if len(values) >= 2:
        return values[:2]
    elif len(values) == 1:
        if values[0] == 'text':
            return 'text', 'plain'
        elif values[0] == 'html':
            return 'text', 'html'
        return 'application', 'octet-stream'


def split(header):
    """Splits value part and parameters part,
    e.g.
         split("MULTIPART/MIXED;boundary=hal_9000")
    becomes:
         ["multipart/mixed", "boundary=hal_9000"]
    """
    match = headerValue.match(header)
    if not match:
        return (None, None)
    return match.group(1).lower(), header[match.end():]


def decode_parameters(string):
    """Parameters can be splitted into several parts, e.g.

    title*0*=us-ascii'en'This%20is%20even%20more%20
    title*1*=%2A%2A%2Afun%2A%2A%2A%20
    title*2="isn't it!"

    decode them to the dictionary with keys and values"""
    parameters = collect_parameters(string)
    groups = {}
    for k, parts in groupby(parameters, get_key):
        groups[k] = concatenate(list(parts))
    return groups


def collect_parameters(rest):
    """Scans the string and collects parts
    that look like parameter, returns deque of strings
    """
    parameters = deque()
    p, rest = match_parameter(rest)
    while p:
        parameters.append(p)
        p, rest = match_parameter(rest)
    return parameters


def concatenate(parts):
    """ Concatenates splitted parts of a parameter in a single parameter,
    e.g.
         URL*0="ftp://";
         URL*1="cs.utk.edu/pub/moore/bulk-mailer/bulk-mailer.tar"

    becomes:

         URL="ftp://cs.utk.edu/pub/moore/bulk-mailer/bulk-mailer.tar"
    """
    part = parts[0]

    if is_old_style(part):
        # old-style parameters do not support any continuations
        return encodedword.mime_to_unicode(get_value(part))
    else:
        return u"".join(
            decode_new_style(p) for p in partition(parts))


def match_parameter(rest):
    for match in (match_old, match_new):
        p, rest = match(rest)
        if p:
            return p, rest
    return (None, rest)


def match_old(rest):
    match = oldStyleParameter.match(rest)
    if match:
        name = match.group('name')
        value = match.group('value')
        return parameter('old', name, value), rest[match.end():]
    else:
        return None, rest


def match_new(rest):
    match = newStyleParameter.match(rest)
    if match:
        name = parse_parameter_name(match.group('name'))
        value = match.group('value')
        return parameter('new', name, value), rest[match.end():]
    else:
        return (None, rest)


def reverse(string):
    """Native reverse of a string looks a little bit cryptic,
    just a readable wrapper"""
    return string[::-1]


def parse_parameter_name(key):
    """New style parameter names can be splitted into parts,
    e.g.

    title*0* means that it's the first part that is encoded
    title*1* means that it's the second part that is encoded
    title*2 means that it is the third part that is unencoded
    title means single unencoded
    title* means single encoded part

    I found it easier to match against a reversed string,
    as regexp is simpler
    """
    m = reverseContinuation.match(reverse(key))
    key = reverse(m.group('key'))
    part= reverse(m.group('part')) if m.group('part') else None
    encoded = m.group('encoded')
    return (key, part, encoded)


def decode_new_style(parameter):
    """Decodes parameter values, quoted or percent encoded, to unicode"""
    if is_quoted(parameter):
        return unquote(parameter)
    if is_encoded(parameter):
        return decode_charset(parameter)
    return get_value(parameter)


def partition(parts):
    """Partitions the parts in accordance to the algo here:
    http://tools.ietf.org/html/rfc2231#section-4.1
    """
    encoded = deque()
    for part in parts:
        if is_encoded(part):
            encoded.append(part)
            continue
        if encoded:
            yield join_parameters(encoded)
            encoded = deque()
        yield part
    if encoded:
        yield join_parameters(encoded)

def decode_charset(parameter):
    """Decodes things like:
    "us-ascii'en'This%20is%20even%20more%20%2A%2A%2Afun%2A%2A%2A%20"
    to unicode """

    v = get_value(parameter)
    parts = v.split("'", 2)
    if len(parts) != 3:
        return v
    charset, language, val = parts
    val = urllib.unquote(val)
    return charsets.convert_to_unicode(charset, val)


def unquote(parameter):
    """Simply removes quotes"""
    return get_value(parameter).strip('"')


def parameter(ptype, key, value):
    """Parameter is stored as a tuple,
    and below are conventional
    """
    return (ptype, key, value)

def is_quoted(part):
    return get_value(part)[0] == '"'

def is_new_style(parameter):
    return parameter[0] == 'new'

def is_old_style(parameter):
    return parameter[0] == 'old'

def is_encoded(part):
    return part[1][2] == '*'

def get_key(parameter):
    if is_old_style(parameter):
        return parameter[1].lower()
    else:
        return parameter[1][0].lower()

def get_value(parameter):
    return parameter[2]

def join_parameters(parts):
    joined = "".join(get_value(p) for p in parts)
    for p in parts:
        return parameter(p[0], p[1], joined)

# used to split header value and parameters
headerValue = re.compile(r"""
       # don't care about the spaces
       ^[\ \t]*
       #main type and sub type or any other value
       ([a-z0-9\-/\.]+)
       # grab the trailing spaces, colons
       [\ \t;]*""", re.IGNORECASE | re.VERBOSE)


oldStyleParameter = re.compile(r"""
     # according to rfc1342, param value can be encoded-word
     # and it's actually very popular, so detect this parameter first
     ^
     # skip spaces
     [\ \t]*
     # parameter name
     (?P<name>
         [^\x00-\x1f\s\(\)<>@,;:\\"/\[\]\?=]+
     )
     # skip spaces
     [\ \t]*
     =
     # skip spaces
     [\ \t]*
     #optional quoting sign
     "?
     # skip spaces
     [\ \t]*
     # and a glorious encoded-word sequence
     (?P<value>
       =\?
       .* # non-greedy to match the end sequence chars
       \?=
     )
     # ends with optional quoting sign that we ignore
     "?
""", re.IGNORECASE | re.VERBOSE)


newStyleParameter = re.compile(r"""
     # Here we grab anything that looks like a parameter
     ^
     # skip spaces
     [\ \t]*
     # parameter name
     (?P<name>
         [^\x00-\x1f\s\(\)<>@,;:\\"/\[\]\?=]+
     )
     # skip spaces
     [\ \t]*
     =
     # skip spaces
     [\ \t]*
     (?P<value>
       (?:
         "(?:
             [\x21\x23-\x5b\x5d-\x7e\ \t]
             |
             (?:\\[\x21-\x7e\t\ ])
          )+"
       )
     |
     # any (US-ASCII) CHAR except SPACE, CTLs, or tspecials
     [^\x00-\x1f\s\(\)<>@,;:\\"/\[\]\?=]+
     )
     # skip spaces
     [\ \t]*
     ;?
""", re.IGNORECASE | re.VERBOSE)

reverseContinuation = re.compile(
    "^(?P<encoded>\*)?(?P<part>\d+\*)?(?P<key>.*)")
