import base64
import io
import re
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from flanker.mime.message.headers import parsing


_BODY_LINES_RE = re.compile(r"\r?\n")


class SimpleCanonicalization(object):
    name = "simple"

    def canonicalize_header(self, header, value):
        return header, value

    def canonicalize_body(self, body):
        return body.rstrip() + "\r\n"


class NoFWSCanonicalization(object):
    _header_fws_re = re.compile(r"[\x09\x20\x0D\x0A]+")
    _body_wsp_re = re.compile(r"[\x09\x20]+")
    _body_orphan_cr_re = re.compile(b"\r([^\n])")

    def canonicalize_header(self, header, value):
        return header, self._header_fws_re.sub("", value) + "\r\n"

    def canonicalize_body(self, body):
        body = self._body_wsp_re.sub("", body)
        body = self._body_orphan_cr_re.sub("\1", body)
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
        message = io.BytesIO(_BODY_LINES_RE.sub("\r\n", message))
        canonicalization = NoFWSCanonicalization()
        signer = self._key.signer(padding.PKCS1v15(), hashes.SHA1())
        h_field = []
        for header_line in parsing.split(message):
            header, value = header_line.split(b":", 1)
            if self._signed_headers is None or header in self._signed_headers:
                h_field.append(header)

                header, value = canonicalization.canonicalize_header(
                    header, value)
                signer.update(header)
                signer.update(b":")
                signer.update(value)
        m = message.read()
        body = canonicalization.canonicalize_body(m)
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
        message = io.BytesIO(_BODY_LINES_RE.sub("\r\n", message))
        signer = self._key.signer(padding.PKCS1v15(), hashes.SHA256())

        h_field = []
        for header_line in parsing.split(message):
            header, value = header_line.split(b":", 1)
            if self._signed_headers is None or header in self._signed_headers:
                h_field.append(header)

                header, value = self._header_canonicalization.canonicalize_header(
                    header, value)
                signer.update(header)
                signer.update(b":")
                signer.update(value)

        h = hashes.Hash(hashes.SHA256(), backend=default_backend())
        h.update(self._body_canonicalization.canonicalize_body(message.read()))
        dkim_header_value = _fold(
            b" a=rsa-sha256; v=1; "
            b"c={header_canonicalization.name}/{body_canonicalization.name}; "
            b"d={domain}; q=dns/txt; s={selector}; t={time}; h={headers}; "
            b"bh={body_hash}; b=".format(
                header_canonicalization=self._header_canonicalization,
                body_canonicalization=self._body_canonicalization,
                domain=self._domain,
                selector=self._selector,
                time=int(time.time()) if current_time is None else current_time,
                headers=": ".join(h_field),
                body_hash=base64.b64encode(h.finalize()),
            )
        )

        dkim_header, dkim_header_value = self._header_canonicalization.canonicalize_header("DKIM-Signature", dkim_header_value)
        signer.update(dkim_header)
        signer.update(b":")
        signer.update(dkim_header_value)
        return b"DKIM-Signature:{dkim_header}{signature}\r\n".format(dkim_header=dkim_header_value, signature=_fold(base64.b64encode(signer.finalize())))



class DKIMVerifier(object):
    def __init__(self, keys):
        self._keys = keys

    def verify(self, message):
        raise NotImplementedError
