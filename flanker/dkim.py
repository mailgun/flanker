import base64
import regex as re
import six
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


_BODY_TRAILING_WSP = re.compile(br"[\t ]+\r\n")
_BODY_WSP_RE = re.compile(br"[\t ]+")


class SimpleCanonicalization(object):
    name = b"simple"

    def canonicalize_header(self, header, value):
        return header, value

    def canonicalize_body(self, body):
        return body.rstrip(b"\r\n") + b"\r\n"


class RelaxedCanonicalization(object):
    name = b"relaxed"

    def canonicalize_header(self, header, value):
        header = header.lower()
        value = _BODY_WSP_RE.sub(b" ", value.replace(b"\r\n", b""))
        return header, value.strip() + b"\r\n"

    def canonicalize_body(self, body):
        body = _BODY_TRAILING_WSP.sub(b"\r\n", body)
        body = _BODY_WSP_RE.sub(b" ", body)
        body = body.rstrip(b"\r\n")
        return body + b"\r\n" if body else b""


class NoFWSCanonicalization(object):
    _header_fws_re = re.compile(br"[\t \r\n]+")
    _body_orphan_cr_re = re.compile(br"\r([^\n])")

    def canonicalize_header(self, header, value):
        return header, self._header_fws_re.sub(b"", value) + b"\r\n"

    def canonicalize_body(self, body):
        body = _BODY_WSP_RE.sub(b"", body)
        body = self._body_orphan_cr_re.sub(br"\1", body)
        body = body.rstrip()
        return body + b"\r\n" if body else b""


def _fold(header):
    """Fold a header line into multiple crlf-separated lines at column 72."""

    i = header.rfind(b"\r\n ")
    if i == -1:
        pre = b""
    else:
        i += 3
        pre = header[:i]
        header = header[i:]
    while len(header) > 72:
        i = header[:72].rfind(b" ")
        if i == -1:
            i = j = 72
        else:
            j = i + 1
        pre += header[:i] + b"\r\n "
        header = header[j:]
    return pre + header


class DomainKeySigner(object):
    def __init__(self, key, selector, domain, signed_headers=None):
        self._key = key

        self._selector = selector
        if six.PY3 and isinstance(selector, six.text_type):
            self._selector = selector.encode('utf-8')

        self._domain = domain
        if six.PY3 and isinstance(domain, six.text_type):
            self._domain = domain.encode('utf-8')

        self._signed_headers = None

    def sign(self, message):
        canonicalization = NoFWSCanonicalization()
        signer = self._key.signer(padding.PKCS1v15(), hashes.SHA1())

        if six.PY3 and isinstance(message, six.text_type):
            message = message.encode('utf-8')

        headers, body = _rfc822_parse(message)

        h_field = []
        for header, value in headers:
            if self._signed_headers is None or header in self._signed_headers:
                h_field.append(header)

                header, value = canonicalization.canonicalize_header(
                    header, value)
                signer.update(header)
                signer.update(b":")
                signer.update(value)
        body = canonicalization.canonicalize_body(body)
        if body:
            signer.update(b"\r\n")
            signer.update(body)

        return _fold(b"DomainKey-Signature: a=rsa-sha1; c=nofws; d=%s; s=%s;"
                     b" q=dns; h=%s; b=%s"
                     % (self._domain,
                        self._selector,
                        b": ".join(h_field),
                        base64.b64encode(signer.finalize()))) + b"\r\n"


class DKIMSigner(object):
    def __init__(self, key, selector, domain,
                 header_canonicalization=SimpleCanonicalization(),
                 body_canonicalization=SimpleCanonicalization(),
                 signed_headers=None):
        self._key = key

        self._selector = selector
        if six.PY3 and isinstance(selector, six.text_type):
            self._selector = selector.encode('utf-8')

        self._domain = domain
        if six.PY3 and isinstance(domain, six.text_type):
            self._domain = domain.encode('utf-8')

        self._header_canonicalization = header_canonicalization
        self._body_canonicalization = body_canonicalization
        self._signed_headers = signed_headers

    def sign(self, message, current_time=None):
        if current_time is None:
            current_time = int(time.time())

        signer = self._key.signer(padding.PKCS1v15(), hashes.SHA256())

        headers, body = _rfc822_parse(message)
        h_field = []
        for header, value in headers:
            if self._signed_headers is None or header in self._signed_headers:
                h_field.append(header)

                h, v = self._header_canonicalization.canonicalize_header(
                    header, value)
                signer.update(h)
                signer.update(b":")
                signer.update(v)

        h = hashes.Hash(hashes.SHA256(), backend=default_backend())
        h.update(self._body_canonicalization.canonicalize_body(body))
        dkim_header_value = _fold(b" a=rsa-sha256; v=1; c=%s/%s; d=%s; "
                                  b"q=dns/txt; s=%s; t=%d; h=%s; bh=%s; b="
                                  % (self._header_canonicalization.name,
                                     self._body_canonicalization.name,
                                     self._domain,
                                     self._selector,
                                     current_time,
                                     b": ".join(h_field),
                                     base64.b64encode(h.finalize())))

        h, v = self._header_canonicalization.canonicalize_header(
            b"DKIM-Signature", dkim_header_value)
        signer.update(h)
        signer.update(b":")
        signer.update(v)
        return b"DKIM-Signature:%s%s\r\n" % (
            v, _fold(base64.b64encode(signer.finalize())))

_RFC822_NEWLINE_RE = re.compile(br"\r?\n")
_RFC822_WS_RE = re.compile(br"[\t ]")
_RFC822_HEADER_RE = re.compile(br"([\x21-\x7e]+?):")


def _rfc822_parse(message):
    headers = []
    lines = _RFC822_NEWLINE_RE.split(message)
    i = 0
    while i < len(lines):
        if len(lines[i]) == 0:
            # End of headers, return what we have plus the body, excluding the
            # blank line.
            i += 1
            break
        if _RFC822_WS_RE.match(lines[i][:1]):
            headers[-1][1] += lines[i] + b"\r\n"
        else:
            m = _RFC822_HEADER_RE.match(lines[i])
            if m is not None:
                headers.append([m.group(1), lines[i][m.end(0):] + b"\r\n"])
            elif lines[i].startswith(b"From "):
                pass
            else:
                raise ValueError("Unexpected characters in RFC822 header: %s"
                                 % lines[i])
        i += 1
    return (headers, b"\r\n".join(lines[i:]))
