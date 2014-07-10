import base64
import regex as re
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


_BODY_TRAILING_WSP = re.compile(r"[\t ]+\r\n")
_BODY_WSP_RE = re.compile(r"[\t ]+")


class SimpleCanonicalization(object):
    name = "simple"

    def canonicalize_header(self, header, value):
        return header, value

    def canonicalize_body(self, body):
        return body.rstrip("\r\n") + "\r\n"


class RelaxedCanonicalization(object):
    name = "relaxed"

    def canonicalize_header(self, header, value):
        header = header.lower()
        value = _BODY_WSP_RE.sub(" ", value.replace("\r\n", ""))
        return header, value.strip() + b"\r\n"

    def canonicalize_body(self, body):
        body = _BODY_TRAILING_WSP.sub("\r\n", body)
        body = _BODY_WSP_RE.sub(" ", body)
        body = body.rstrip("\r\n")
        return body + b"\r\n" if body else b""


class NoFWSCanonicalization(object):
    _header_fws_re = re.compile(r"[\t \r\n]+")
    _body_orphan_cr_re = re.compile(b"\r([^\n])")

    def canonicalize_header(self, header, value):
        return header, self._header_fws_re.sub("", value) + "\r\n"

    def canonicalize_body(self, body):
        body = _BODY_WSP_RE.sub("", body)
        body = self._body_orphan_cr_re.sub(r"\1", body)
        body = body.rstrip()
        return body + "\r\n" if body else ""


def _fold(header):
    """Fold a header line into multiple crlf-separated lines at column 72."""

    i = header.rfind("\r\n ")
    if i == -1:
        pre = ""
    else:
        i += 3
        pre = header[:i]
        header = header[i:]
    while len(header) > 72:
        i = header[:72].rfind(" ")
        if i == -1:
            i = j = 72
        else:
            j = i + 1
        pre += header[:i] + "\r\n "
        header = header[j:]
    return pre + header


class DomainKeySigner(object):
    def __init__(self, key, selector, domain, signed_headers=None):
        self._key = key
        self._selector = selector
        self._domain = domain
        self._signed_headers = None

    def sign(self, message):
        canonicalization = NoFWSCanonicalization()
        signer = self._key.signer(padding.PKCS1v15(), hashes.SHA1())

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

        return _fold(
            b"DomainKey-Signature: a=rsa-sha1; c=nofws; d={domain}; "
            b"s={selector}; q=dns; h={headers}; b={signature}".format(
                domain=self._domain,
                selector=self._selector,
                headers=b": ".join(h_field),
                signature=base64.b64encode(signer.finalize())
            )) + b"\r\n"


class DKIMSigner(object):
    def __init__(self, key, selector, domain,
                 header_canonicalization=SimpleCanonicalization(),
                 body_canonicalization=SimpleCanonicalization(),
                 signed_headers=None):
        self._key = key
        self._selector = selector
        self._domain = domain
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
        dkim_header_value = _fold(
            b" a=rsa-sha256; v=1; "
            b"c={header_canonicalization.name}/{body_canonicalization.name}; "
            b"d={domain}; q=dns/txt; s={selector}; t={time}; h={headers}; "
            b"bh={body_hash}; b=".format(
                header_canonicalization=self._header_canonicalization,
                body_canonicalization=self._body_canonicalization,
                domain=self._domain,
                selector=self._selector,
                time=current_time,
                headers=": ".join(h_field),
                body_hash=base64.b64encode(h.finalize()),
            )
        )

        h, v = self._header_canonicalization.canonicalize_header(
            "DKIM-Signature", dkim_header_value)
        signer.update(h)
        signer.update(b":")
        signer.update(v)
        return b"DKIM-Signature:{dkim_header}{signature}\r\n".format(
            dkim_header=v,
            signature=_fold(base64.b64encode(signer.finalize()))
        )

_RFC822_NEWLINE_RE = re.compile(r"\r?\n")
_RFC822_WS_RE = re.compile(r"[\t ]")
_RFC822_HEADER_RE = re.compile(r"([\x21-\x7e]+?):")


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
        if _RFC822_WS_RE.match(lines[i][0]):
            headers[-1][1] += lines[i] + "\r\n"
        else:
            m = _RFC822_HEADER_RE.match(lines[i])
            if m is not None:
                headers.append([m.group(1), lines[i][m.end(0):] + "\r\n"])
            elif lines[i].startswith("From "):
                pass
            else:
                raise ValueError(
                    "Unexpected characters in RFC822 header: %s" % lines[i]
                )
        i += 1
    return (headers, "\r\n".join(lines[i:]))
