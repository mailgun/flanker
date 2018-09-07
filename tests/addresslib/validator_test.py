# coding:utf-8

import re

from .. import *

import six
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest
from mock import patch

from flanker.addresslib import address, validate


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


@nottest
def fake_dns_lookup(domain_name, lookup_results):
    if six.PY3:
        # This is how `dnsq` actually returns mx_records. Emulating it in tests
        lookup_results = filter(lambda x: True, lookup_results)

    fqdn = '%s.' % domain_name
    return {
        fqdn: lookup_results,
    }


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
        with patch.object(address, 'mail_exchanger_lookup') as mock_method:
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
        with patch.object(address, 'mail_exchanger_lookup') as mock_method:
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
    all_invalid_list = invalid_domain_list + invalid_subdomain_list + invalid_tld_list + invalid_mx_list
    all_list = all_valid_list + all_invalid_list

    # all valid
    with patch.object(address, 'mail_exchanger_lookup') as mock_method:
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
        parse, unpar = address.validate_list(invalid_mx_list, as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_mx_list)

        parse, unpar = address.validate_list(invalid_tld_list, as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_tld_list)

        parse, unpar = address.validate_list(invalid_domain_list, as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_domain_list)

        parse, unpar = address.validate_list(invalid_subdomain_list, as_tuple=True)
        assert_equal(parse, [])
        assert_equal(unpar, invalid_subdomain_list)

        parse, unpar = address.validate_list(all_list, as_tuple=True)
        assert_equal(parse, all_valid_list)
        assert_equal(unpar, all_invalid_list)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate._get_dns_lookup')
def test_mx_lookup(dns, cmx):
    domain_name = 'mailgun.com'
    mx_records = ['mx1.fake.mailgun.com', 'mx2.fake.mailgun.com']
    email_address = 'username@%s' % domain_name
    expected_address = email_address

    dns.return_value = fake_dns_lookup(domain_name, mx_records)
    cmx.return_value = 'mx1.fake.mailgun.com'

    validated_address = address.validate_address(email_address)
    assert_not_equal(validated_address, None)
    assert_equal(validated_address, expected_address)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate._get_dns_lookup')
def test_mx_lookup_has_mx_has_fallback(dns, cmx):
    # has fallback A, has MX server
    domain_name = 'domain.com'
    mx_records = ['domain.com']
    email_address = 'username@%s' % domain_name
    expected_address = email_address

    dns.return_value = fake_dns_lookup(domain_name, mx_records)
    cmx.return_value = 'domain.com'

    addr = address.validate_address(email_address)
    assert_not_equal(addr, None)
    assert_equal(addr, expected_address)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate._get_dns_lookup')
def test_mx_lookup_has_mx_no_server_answer(dns, cmx):
    # has MX, no server answers
    domain_name = 'example.com'
    mx_records = ['mx.example.com']
    email_address = 'username@%s' % domain_name

    dns.return_value = fake_dns_lookup(domain_name, mx_records)
    cmx.return_value = None

    addr = address.validate_address(email_address)
    assert_equal(addr, None)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate._get_dns_lookup')
def test_mx_lookup_has_no_mx(dns, cmx):
    # no MX
    domain_name = 'example.com'
    email_address = 'username@%s' % domain_name
    dns.return_value = fake_dns_lookup(domain_name, [])
    cmx.return_value = None

    addr = address.validate_address(email_address)
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
    with patch.object(address, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        parse, metrics = address.validate_address('foo@example.com', metrics=True)

        assert_not_equal(metrics, None)
        assert_equal(metrics['mx_lookup'], 10)
        assert_equal(metrics['dns_lookup'], 20)
        assert_equal(metrics['mx_conn'], 30)


# @patch('flanker.addresslib.validate.connect_to_mail_exchanger')
# @patch('flanker.addresslib.validate.lookup_domain')
# @patch('flanker.addresslib.validate.lookup_exchanger_in_cache')
# def test_validate_domain_literal(mock_lookup_exchanger_in_cache, mock_lookup_domain, mock_connect_to_mail_exchanger):
#     mock_lookup_exchanger_in_cache.return_value = (False, None)
#     mock_connect_to_mail_exchanger.return_value = '1.2.3.4'
#
#     addr = address.validate_address('foo@[1.2.3.4]')
#
#     assert_equal(addr.full_spec(), 'foo@[1.2.3.4]')
#     mock_lookup_domain.assert_not_called()
#     mock_connect_to_mail_exchanger.assert_called_once_with(['1.2.3.4'])


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate.lookup_domain')
def test_mx_yahoo_dual_lookup(ld, cmx):
    ld.return_value = ['mta7.am0.yahoodns.net', 'mta6.am0.yahoodns.net']
    cmx.return_value = 'mta5.am0.yahoodns.net'

    # Invalidate managed email response out of pattern
    mailbox = '1testuser@yahoo.com'
    addr = address.validate_address(mailbox)
    assert_equal(type(addr), type(None))

    # Same test but with validate_list
    addr = address.validate_list([mailbox])
    expected = 'flanker.addresslib.address:'
    assert_equal(addr, [])

    # Allow Yahoo MX unmanaged mailboxes to pass remaining patterns
    mailbox = '8testuser@frontier.com'
    addr = address.validate_address(mailbox)
    assert_equal(addr, mailbox)

    # Same test but with validate_list
    expected = 'flanker.addresslib.address:'
    addr = address.validate_list([mailbox])
    assert_equal(addr, mailbox)


def test_mx_yahoo_manage_flag_toggle():
    # Just checking if the domain provided from the sub is managed
    mailbox = '1testuser@yahoo.com'
    addr_obj = address.parse(mailbox)
    managed = validate.yahoo.managed_email(addr_obj.hostname)
    assert_equal(managed, True)

    # Same but inversed, unmanaged yahoo mailbox
    mailbox = '1testuser@frontier.com'
    addr_obj = address.parse(mailbox)
    managed = validate.yahoo.managed_email(addr_obj.hostname)
    assert_equal(managed, False)


@patch('flanker.addresslib.validate.connect_to_mail_exchanger')
@patch('flanker.addresslib.validate.lookup_domain')
def test_mx_aol_dual_lookup(ld, cmx):
    ld.return_value = ['mailin-01.mx.aol.com', 'mailin-02.mx.aol.com']
    cmx.return_value = 'mailin-03.mx.aol.com'

    # Invalidate managed email response out of pattern
    mailbox = '1testuser@aol.com'
    addr = address.validate_address(mailbox)
    assert_equal(type(addr), type(None))

    # Same test but with validate_list
    addr = address.validate_list([mailbox])
    expected = 'flanker.addresslib.address:'
    assert_equal(addr, [])

    # Allow AOL MX unmanaged mailboxes to pass remaining patterns
    mailbox = '8testuser@verizon.net'
    addr = address.validate_address(mailbox)
    assert_equal(addr, mailbox)

    # Same test but with validate_list
    expected = 'flanker.addresslib.address:'
    addr = address.validate_list([mailbox])
    assert_equal(addr, mailbox)


def test_mx_aol_manage_flag_toggle():
    # Just checking if the domain provided from the sub is managed
    mailbox = '1testuser@aol.com'
    addr_obj = address.parse(mailbox)
    unmanaged = validate.aol.unmanaged_email(addr_obj.hostname)
    assert_equal(unmanaged, False)

    # Same but inversed, unmanaged aol mailbox
    mailbox = '1testuser@verizon.net'
    addr_obj = address.parse(mailbox)
    unmanaged = validate.aol.unmanaged_email(addr_obj.hostname)
    assert_equal(unmanaged, True)


def test_bad_tld():
    # con is not a valid TLD
    addr_spec = 'test@example.con'
    addr_obj, metrics = address.validate_address(
        addr_spec, skip_remote_checks=True, metrics=True
    )
    assert_equal(addr_obj, None)
    assert_not_equal(metrics['tld_lookup'], 0)

    # example is not a valid TLD
    addr_spec = 'test@example'
    addr_obj, metrics = address.validate_address(
        addr_spec, skip_remote_checks=True, metrics=True
    )
    assert_equal(addr_obj, None)
    assert_not_equal(metrics['tld_lookup'], 0)
