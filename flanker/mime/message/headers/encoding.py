import email.message
import flanker.addresslib.address
import logging

from collections import deque
from email.header import Header
from flanker.mime.message.headers import parametrized
from flanker.utils import to_utf8

log = logging.getLogger(__name__)

# max length for a header line is 80 chars
# max recursion depth is 1000
# 80 * 1000 for header is too much for the system
# so we allow just 100 lines for header 
MAX_HEADER_LENGTH = 8000

ADDRESS_HEADERS = ('From', 'To', 'Delivered-To', 'Cc', 'Bcc', 'Reply-To')

def to_mime(key, value):
    if not value:
        return ""

    if type(value) == list:
        return "; ".join(encode(key, v) for v in value)
    else:
        return encode(key, value)


def encode(name, value):
    try:
        if parametrized.is_parametrized(name, value):
            value, params = value
            return encode_parametrized(name, value, params)
        else:
            return encode_unstructured(name, value)
    except Exception:
        log.exception("Failed to encode %s %s" % (name, value))
        raise


def encode_unstructured(name, value):
    if len(value) > MAX_HEADER_LENGTH:
        return to_utf8(value)
    try:
        return Header(
            value.encode("ascii"), "ascii", header_name=name).encode(
            splitchars=' ;,')
    except UnicodeEncodeError:
        if is_address_header(name, value):
            return encode_address_header(name, value)
        else:
            return Header(
                value.encode("utf-8"), "utf-8", header_name=name).encode(
                splitchars=' ;,')


def encode_address_header(name, value):
    out = deque()
    for addr in flanker.addresslib.address.parse_list(value):
        out.append(addr.full_spec())
    return "; ".join(out)


def encode_parametrized(key, value, params):
    if params:
        params = [encode_param(key, n, v) for n, v in params.iteritems()]
        return value + "; " + ("; ".join(params))
    else:
        return value


def encode_param(key, name, value):
    try:
        value = value.encode("ascii")
        return email.message._formatparam(name, value)
    except Exception:
        value = Header(
            value.encode("utf-8"), "utf-8", header_name=key).encode(splitchars=' ;,')
        return email.message._formatparam(name, value)


def encode_string(name, value):
    try:
        return Header(
            value.encode("ascii"), "ascii", header_name=name).encode(splitchars=' ;,')
    except UnicodeEncodeError:
        return Header(
            value.encode("utf-8"), "utf-8", header_name=name).encode(splitchars=' ;,')


def is_address_header(key, val):
    return key in ADDRESS_HEADERS and '@' in val
