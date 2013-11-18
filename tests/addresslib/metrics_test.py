# coding:utf-8

from .. import *
from mock import patch
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from flanker.addresslib import address, validate

@nottest
def mock_exchanger_lookup(arg, metrics=False):
    mtimes = {'mx_lookup': 10, 'dns_lookup': 20, 'mx_conn': 30}
    if metrics is True:
        if arg == 'ai' or arg == 'mailgun.org' or arg == 'fakecompany.mailgun.org':
            return ('', mtimes)
        else:
            return (None, mtimes)
    else:
        if arg == 'ai' or arg == 'mailgun.org' or arg == 'fakecompany.mailgun.org':
            return ''
        else:
            return None


def test_metrics_parse():
    # parse
    assert_equal(len(address.parse('foo@example.com', metrics=True)), 2)
    p, m = address.parse('foo@example.com', metrics=True)
    assert_equal('parsing' in m, True)
    assert_equal(isinstance(address.parse('foo@example.com', metrics=False), address.EmailAddress), True)
    assert_equal(isinstance(address.parse('foo@example.com'), address.EmailAddress), True)

def test_metrics_parse_list():
    # parse_list
    assert_equal(len(address.parse_list('foo@example.com, bar@example.com', metrics=True)), 2)
    p, m = address.parse_list('foo@example.com, bar@example.com', metrics=True)
    assert_equal('parsing' in m, True)
    assert_equal(isinstance(address.parse_list('foo@example.com, bar@example.com', metrics=False), address.AddressList), True)
    assert_equal(isinstance(address.parse_list('foo@example.com, bar@example.com'), address.AddressList), True)

def test_metrics_validate_address():
    # validate
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        assert_equal(len(address.validate_address('foo@mailgun.net', metrics=True)), 2)
        p, m = address.validate_address('foo@mailgun.net', metrics=True)
        assert_equal('parsing' in m, True)
        assert_equal('mx_lookup' in m, True)
        assert_equal('dns_lookup' in m, True)
        assert_equal('mx_conn' in m, True)
        assert_equal('custom_grammar' in m, True)
        assert_equal(isinstance(address.validate_address('foo@mailgun.org', metrics=False), address.EmailAddress), True)
        assert_equal(isinstance(address.validate_address('foo@mailgun.org'), address.EmailAddress), True)

def test_metrics_validate_list():
    # validate_list
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        assert_equal(len(address.validate_list('foo@mailgun.org, bar@mailgun.org', metrics=True)), 2)
        p, m = address.validate_list('foo@mailgun.org, bar@mailgun.org', metrics=True)
        assert_equal('parsing' in m, True)
        assert_equal('mx_lookup' in m, True)
        assert_equal('dns_lookup' in m, True)
        assert_equal('mx_conn' in m, True)
        assert_equal('custom_grammar' in m, True)
        assert_equal(isinstance(address.validate_list('foo@mailgun.org, bar@mailgun.org', metrics=False), address.AddressList), True)
        assert_equal(isinstance(address.validate_list('foo@mailgun.org, bar@mailgun.org'), address.AddressList), True)
