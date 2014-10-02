# coding:utf-8

import re

from .. import *

from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest
from mock import patch

from flanker.addresslib import address
from flanker.addresslib import validate


COMMENT = re.compile(r'''\s*#''')


@nottest
def valid_localparts(strip_delimiters=False):
    for line in ABRIDGED_LOCALPART_VALID_TESTS.split('\n'):
        # strip line, skip over empty lines
        line = line.strip()
        if line == '':
            continue

        # skip over comments or empty lines
        match = COMMENT.match(line)
        if match:
            continue

        # skip over localparts with delimiters
        if strip_delimiters:
            if ',' in line or ';' in line:
                continue

        yield line

@nottest
def invalid_localparts(strip_delimiters=False):
    for line in ABRIDGED_LOCALPART_INVALID_TESTS.split('\n'):
        # strip line, skip over empty lines
        line = line.strip()
        if line == '':
            continue

        # skip over comments
        match = COMMENT.match(line)
        if match:
            continue

        # skip over localparts with delimiters
        if strip_delimiters:
            if ',' in line or ';' in line:
                continue

        yield line

@nottest
def mock_exchanger_lookup(arg, metrics=False):
    mtimes = {'mx_lookup': 10, 'dns_lookup': 20, 'mx_conn': 30}
    if metrics is True:
        if arg in ['ai', 'mailgun.org', 'fakecompany.mailgun.org']:
            return ('', mtimes)
        else:
            return (None, mtimes)
    else:
        if arg in ['ai', 'mailgun.org', 'fakecompany.mailgun.org']:
            return ''
        else:
            return None

def test_abridged_mailbox_valid_set():
    for line in ABRIDGED_LOCALPART_VALID_TESTS.split('\n'):
        # strip line, skip over empty lines
        line = line.strip()
        if line == '':
            continue

        # skip over comments or empty lines
        match = COMMENT.match(line)
        if match:
            continue

        # mocked valid dns lookup for tests
        with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
            mock_method.side_effect = mock_exchanger_lookup

            addr = line + '@ai'
            mbox = address.validate_address(addr)
            assert_not_equal(mbox, None)

            # domain
            addr = line + '@mailgun.org'
            mbox = address.validate_address(addr)
            assert_not_equal(mbox, None)

            # subdomain
            addr = line + '@fakecompany.mailgun.org'
            mbox = address.validate_address(addr)
            assert_not_equal(mbox, None)


def test_abridged_mailbox_invalid_set():
    for line in ABRIDGED_LOCALPART_INVALID_TESTS.split('\n'):
        # strip line, skip over empty lines
        line = line.strip()
        if line == '':
            continue

        # skip over comments
        match = COMMENT.match(line)
        if match:
            continue

        # mocked valid dns lookup for tests
        with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
            mock_method.side_effect = mock_exchanger_lookup

            addr = line + '@ai'
            mbox = address.validate_address(addr)
            assert_equal(mbox, None)

            # domain
            addr = line + '@mailgun.org'
            mbox = address.validate_address(addr)
            assert_equal(mbox, None)

            # subdomain
            addr = line + '@fakecompany.mailgun.org'
            mbox = address.validate_address(addr)
            assert_equal(mbox, None)


def test_parse_syntax_only_false():
    # syntax + validation
    valid_tld_list = [i + '@ai' for i in valid_localparts()]
    valid_domain_list = [i + '@mailgun.org' for i in valid_localparts()]
    valid_subdomain_list = [i + '@fakecompany.mailgun.org' for i in valid_localparts()]

    invalid_mx_list = [i + '@example.com' for i in valid_localparts(True)]
    invalid_tld_list = [i + '@com' for i in invalid_localparts(True)]
    invalid_domain_list = [i + '@example.com' for i in invalid_localparts(True)]
    invalid_subdomain_list = [i + '@sub.example.com' for i in invalid_localparts(True)]

    all_valid_list = valid_tld_list + valid_domain_list + valid_subdomain_list
    all_invalid_list = invalid_mx_list + invalid_tld_list + invalid_domain_list + \
        invalid_subdomain_list
    all_list = all_valid_list + all_invalid_list

    # all valid
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        parse, unpar = address.validate_list(', '.join(valid_tld_list), as_tuple=True)
        assert_equal(parse, valid_tld_list)
        assert_equal(unpar, [])

        parse, unpar = address.validate_list(', '.join(valid_domain_list), as_tuple=True)
        assert_equal(parse, valid_domain_list)
        assert_equal(unpar, [])

        parse, unpar = address.validate_list(', '.join(valid_subdomain_list), as_tuple=True)
        assert_equal(parse, valid_subdomain_list)
        assert_equal(unpar, [])

        # all invalid
        parse, unpar = address.validate_list(', '.join(invalid_mx_list), as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_mx_list)

        parse, unpar = address.validate_list(', '.join(invalid_tld_list), as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_tld_list)

        parse, unpar = address.validate_list(', '.join(invalid_domain_list), as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_domain_list)

        parse, unpar = address.validate_list(', '.join(invalid_subdomain_list), as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_subdomain_list)

        parse, unpar = address.validate_list(', '.join(all_list), as_tuple=True)
        assert_equal(parse, all_valid_list)
        assert_equal(unpar, all_invalid_list)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate.lookup_domain')
def test_mx_lookup(ld, cmx):
    # has MX, has MX server
    ld.return_value = ['mx1.fake.mailgun.com', 'mx2.fake.mailgun.com']
    cmx.return_value = 'mx1.fake.mailgun.com'

    addr = address.validate_address('username@mailgun.com')
    assert_not_equal(addr, None)

    # has fallback A, has MX server
    ld.return_value = ['domain.com']
    cmx.return_value = 'domain.com'

    addr = address.validate_address('username@domain.com')
    assert_not_equal(addr, None)

    # has MX, no server answers
    ld.return_value = ['mx.example.com']
    cmx.return_value = None

    addr = address.validate_address('username@example.com')
    assert_equal(addr, None)

    # no MX
    ld.return_value = []
    cmx.return_value = None

    addr = address.validate_address('username@no-dns-records-for-domain.com')
    assert_equal(addr, None)


def test_mx_lookup_metrics():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        a, metrics = validate.mail_exchanger_lookup('example.com', metrics=True)
        assert_equal(metrics['mx_lookup'], 10)
        assert_equal(metrics['dns_lookup'], 20)
        assert_equal(metrics['mx_conn'], 30)

        # ensure values are unpacked correctly
        a = validate.mail_exchanger_lookup('example.com', metrics=False)
        a = validate.mail_exchanger_lookup('example.com', metrics=False)

def test_validate_address_metrics():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        parse, metrics = address.validate_address('foo@example.com', metrics=True)

        assert_not_equal(metrics, None)
        assert_equal(metrics['mx_lookup'], 10)
        assert_equal(metrics['dns_lookup'], 20)
        assert_equal(metrics['mx_conn'], 30)
