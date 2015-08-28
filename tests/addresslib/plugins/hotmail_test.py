# coding:utf-8

import random
import string

from flanker.addresslib import address
from flanker.addresslib import validate

from mock import patch
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from ... import skip_if_asked

DOMAIN = '@hotmail.com'
SAMPLE_MX = 'mx0.hotmail.com'

@nottest
def mock_exchanger_lookup(arg, metrics=False):
    mtimes = {'mx_lookup': 0, 'dns_lookup': 0, 'mx_conn': 0}
    return (SAMPLE_MX, mtimes)


def test_exchanger_lookup():
    '''
    Test if exchanger lookup is occuring correctly. If this simple test
    fails that means custom grammar was hit. Then the rest of the tests
    can be mocked. Should always be run during deployment, can be skipped
    during development.
    '''
    skip_if_asked()

    # very simple test that should fail Hotmail custom grammar
    addr_string = '!mailgun' + DOMAIN
    addr = address.validate_address(addr_string)
    assert_equal(addr, None)


def test_hotmail_pass():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # valid length range
        for i in range(1, 65):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # start must be letter or number
        for i in string.ascii_letters + string.digits:
            localpart = str(i) + 'a'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # end must be letter or number
        for i in string.ascii_letters + string.digits + '-_':
            localpart = 'a' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # must be letter, num, period, hyphen, or underscore
        for i in string.ascii_letters + string.digits + '.-_':
            localpart = 'a' + str(i) + '0'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # only zero or one plus allowed
        for i in range(0, 2):
            localpart = 'aa' + '+'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # allow multiple periods
        localpart = 'aa.bb.00'
        addr = address.validate_address(localpart + DOMAIN)
        assert_not_equal(addr, None)


def test_hotmail_fail():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # invalid length range
        for i in range(0, 0) + range(65, 70):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid start char (must start with letter)
        for i in string.punctuation:
            localpart = str(i) + 'a'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid end char (must end with letter or num, hyphen, or underscore)
        invalid_end_chars = string.punctuation
        invalid_end_chars = invalid_end_chars.replace('-', '')
        invalid_end_chars = invalid_end_chars.replace('_', '')
        invalid_end_chars = invalid_end_chars.replace('+', '')
        for i in invalid_end_chars:
            localpart = 'a' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid chars (must be letter, num, underscore, or dot)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('.', '')
        invalid_chars = invalid_chars.replace('-', '')
        invalid_chars = invalid_chars.replace('_', '')
        invalid_chars = invalid_chars.replace('+', '')
        for i in invalid_chars:
            localpart = 'a' + str(i) + '0'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # no more than 1 consecutive dot (.) or plus (+) allowed
        for i in range(2, 4):
            localpart = 'aa' + '.'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

            localpart = 'aa' + '+'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)
