import glob
import io
import os

import six
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from nose.tools import assert_equal

from flanker import dkim


DUMMY_EMAIL = b"""
From: Joe SixPack <joe@football.example.com>
To: Suzie Q <suzie@shopping.example.net>
Subject: Is dinner ready?
Date: Fri, 11 Jul 2003 21:00:37 -0700 (PDT)
Message-ID: <20030712040037.46341.5F8J@football.example.com>

Hi.

We lost the game.  Are you hungry yet?

Joe.
""".strip()

DUMMY_RSA_KEY = serialization.load_pem_private_key(b"""
-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDn09PV9KPE7Q+N5K5UtNLT1DLl8z/pKM2pP5tXqWx2OsEw00lC
kDHdHESwzS050s/8rtkERKKyusCzCm9+vC1pQzUlmtibfF4PQAQc1pJL6KHqlidg
Hw49atYmnC25CaeXt65pAYXoIacOZ8k5X7FW3Eagex8nG0iMw4ObOtg6CwIDAQAB
AoGBAL31l/4YYN1rNrSZLrQgGyUSGsbLxJHEKolFon95R3O1fzoH117gkstQb4TE
Cwv3jw/JIfBaYUq8tku/AE9D2Jx51x7kYaCuQIMTavKIgkXKfxTQCQDjSEfkvXMW
4WOIj5sYdSCNbzLbaeFsWG32bSsBTy/sSheDIlCEFnqDuqwBAkEA+wYfJEMDf5nS
VCQd9VKGM4HVeTWBioaWBFCflFdhc1Vb65dsNDp8iIMZgAHC2LEX5dMUmgqXk7AT
lwFlIeW4CwJBAOxsSfuIVMuPKyx1xQ6ebpC7zeVxIOdswcM8ain91MSGDdKZw6pF
ioFh3kUbKHw4yqqHbdRmUDAJ1mcgGJQOxgECQQCmQaGylKfmhWymyd0FtIip6J4I
z4ViyEznwrZOu6kRiEF/QiUqWmpMx/fFrmTsvC5Fy43jkIxgBsiSxRvEXa+NAkB+
5m0bhwTEslchKSGZhC6inzuYAQ4BSh4C1mXBnk5bIf0/Ymtk9KiwY8CzZS1o5+7Y
c5LfI/+8mTss5UxsBDYBAkEA6NqhcsNWndIJZiWUU4u+RjFUQXqH8WCyJmEDCNxs
7SGRS1DTUGX4Y70m9dQpguy6Zg+gpHC+o+ERZR06uEQr+w==
-----END RSA PRIVATE KEY-----
""", password=None, backend=default_backend())


def test_simple_domain_key_signature():
    signer = dkim.DomainKeySigner(DUMMY_RSA_KEY, "mx", "testing1")
    sig = signer.sign(DUMMY_EMAIL)
    assert_equal(
        sig,
        b"DomainKey-Signature: a=rsa-sha1; c=nofws; d=testing1; s=mx; q=dns;\r"
        b"\n h=From: To: Subject: Date: Message-ID;\r\n b=NDj4joHi27ePRug/aCgy"
        b"wVFaAzxkcWP+F9r5J/gj7SHd1dFB3YfyZIYmnc+xo/HTN425sj\r\n njfKMRjSLNugH"
        b"i2SN1doNsdHigD7hnXwzoRVaZQ15zWNcQwaHriaTyijV+PUHEeU/EdNSakv\r\n XDoo"
        b"7lzEjzaYxBDx2PP25abuTSJF0=\r\n"
    )

def test_simple_dkim_signature():
    signer = dkim.DKIMSigner(DUMMY_RSA_KEY, "mx", "testing1")
    sig = signer.sign(DUMMY_EMAIL, current_time=1404859754)
    print(sig)
    assert_equal(
        sig,
        b"DKIM-Signature: a=rsa-sha256; v=1; c=simple/simple; d=testing1; q=dn"
        b"s/txt; s=mx;\r\n t=1404859754; h=From: To: Subject: Date: Message-ID"
        b";\r\n bh=4bLNXImK9drULnmePzZNEBleUanJCX5PIsDIFoH4KTQ=; b=IrtWacnHcpq"
        b"elwoPBxtI9RY0qJ9ABdltZRJcf5wXjXwA7sCbuxibMWk4m81m2zGqMOBsziIE\r\n 0j"
        b"Jxf4OJGbWVXwSB2mNPfPyScpqJEL+z43vhx+/ZTWBWpj3TSAuHmOT4G7wrySLAZmfDcm"
        b"je\r\n J00EP9NPpJOz2oUI8NJwozkUr6k=\r\n"
    )


def test_canonicalization():
    path = os.path.join(
        os.path.dirname(__file__), "fixtures", "messages", "dkim", "email.*"
    )
    for i, path in enumerate(glob.glob(path)):
        with open(path, 'rb') as f:
            contents = f.read()
        with open(path.replace("email", "nofws.expected"), 'rb') as f:
            nofws_contents = f.read()
        with open(path.replace("email", "simple.expected"), 'rb') as f:
            simple_contents = f.read()
        with open(path.replace("email", "relaxed.expected"), 'rb') as f:
            relaxed_contents = f.read()

        print('Test case #%d: %s' % (i, path))

        assert_equal(
            canonicalize_contents(dkim.NoFWSCanonicalization(), contents),
            nofws_contents
        )
        assert_equal(
            canonicalize_contents(dkim.SimpleCanonicalization(), contents),
            simple_contents
        )
        assert_equal(
            canonicalize_contents(dkim.RelaxedCanonicalization(), contents),
            relaxed_contents
        )


def canonicalize_contents(canonicalization_rule, contents):
    if six.PY3 and isinstance(contents, six.text_type):
        contents = contents.encode('utf-8')

    headers, body = dkim._rfc822_parse(contents)
    output = io.BytesIO()
    for header, value in headers:
        header, value = canonicalization_rule.canonicalize_header(
            header, value)
        output.write(("%s:%s" % (header.decode('utf-8'),
                                 value.decode('utf-8'))).encode('utf-8'))
    body = canonicalization_rule.canonicalize_body(body)
    output.write(b"\r\n")
    output.write(body)
    return output.getvalue()


def _normalize_crlf(s):
    return s.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
