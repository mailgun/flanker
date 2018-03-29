import email.message
import logging
from collections import deque
from email.header import Header

import six

import flanker.addresslib.address
from flanker.mime.message.headers import parametrized
from flanker.mime.message.utils import to_utf8

_log = logging.getLogger(__name__)

_ADDRESS_HEADERS = ('From', 'To', 'Delivered-To', 'Cc', 'Bcc', 'Reply-To')


def to_mime(key, value):
    if not value:
        return ""

    if type(value) == list:
        return "; ".join(encode(key, v) for v in value)

    return encode(key, value)


def encode(name, value):
    try:
        if parametrized.is_parametrized(name, value):
            value, params = value
            return _encode_parametrized(name, value, params)

        return _encode_unstructured(name, value)
    except Exception:
        _log.exception("Failed to encode %s %s" % (name, value))
        raise


def _encode_unstructured(name, value):
    try:
        return Header(
            value.encode("ascii"), "ascii",
            header_name=name).encode(splitchars=' ;,')
    except (UnicodeEncodeError, UnicodeDecodeError):
        if _is_address_header(name, value):
            return _encode_address_header(name, value)

        return Header(
            to_utf8(value), "utf-8",
            header_name=name).encode(splitchars=' ;,')


def _encode_address_header(name, value):
    out = deque()
    for addr in flanker.addresslib.address.parse_list(value):
        if addr.requires_non_ascii():
            out.append(addr.to_unicode().encode('utf-8'))
        else:
            out.append(addr.full_spec().encode('utf-8'))
    return '; '.join(out)


def _encode_parametrized(key, value, params):
    if params:
        params = [_encode_param(key, n, v) for n, v in six.iteritems(params)]
        return value + "; " + ("; ".join(params))

    return value


def _encode_param(key, name, value):
    try:
        if six.PY2:
            value = value.encode('ascii')

        return email.message._formatparam(name, value)
    except Exception:
        value = Header(value.encode("utf-8"), "utf-8",  header_name=key).encode(splitchars=' ;,')
        return email.message._formatparam(name, value)


def encode_string(name, value, maxlinelen=None):
    try:
        header = Header(value.encode("ascii"), "ascii", maxlinelen,
                        header_name=name)
    except UnicodeEncodeError:
        header = Header(value.encode("utf-8"), "utf-8", header_name=name)

    return header.encode(splitchars=' ;,')


def _is_address_header(key, val):
    return key in _ADDRESS_HEADERS and '@' in val
