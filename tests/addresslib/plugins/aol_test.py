# coding:utf-8

import random
import string

from flanker.addresslib import address
from flanker.addresslib import validate

from mock import patch
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from ... import skip_if_asked

DOMAIN = '@aol.com'
SAMPLE_MX = 'sample.mx.aol.com'

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

    # very simple test that should fail AOL custom grammar
    addr_string = '!mailgun' + DOMAIN
    addr = address.validate_address(addr_string)
    assert_equal(addr, None)


def test_aol_pass():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # valid length range
        for i in range(3, 33):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # start must be letter
        for i in string.ascii_letters:
            localpart = str(i) + 'aaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # end must be letter or number
        for i in string.ascii_letters + string.digits:
            localpart = 'aaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # must be letter, num, dot (.), or underscore
        for i in string.ascii_letters + string.digits + '._':
            localpart = 'aa' + str(i) + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # only zero or one dot (.) allowed
        for i in range(0, 2):
            localpart = 'aa' + '.'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)


def test_aol_fail():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # invalid length range
        for i in range(0, 3) + range(33, 40):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid start char (must start with letter)
        for i in string.punctuation + string.digits:
            localpart = str(i) + 'aaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid end char (must end with letter or digit)
        for i in string.punctuation:
            localpart = 'aaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid chars (must be letter, num, underscore, or dot)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('.', '')
        invalid_chars = invalid_chars.replace('_', '')
        for i in invalid_chars:
            localpart = 'aa' + str(i) + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # no more than 1 dot (.) allowed
        for i in range(2, 4):
            localpart = 'aa' + '.'*i + 'a' + '.'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # no consecutive: underscore (_) or dot-underscore (._)
        # or underscore-dot (_.)
        for i in range(1, 4):
            localpart = 'aa' + '__'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

            localpart = 'aa' + '._'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

            localpart = 'aa' + '._'*i + '00'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)
