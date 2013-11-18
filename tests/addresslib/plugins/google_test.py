# coding:utf-8

import random
import string

from flanker.addresslib import address
from flanker.addresslib import validate

from mock import patch
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from ... import skip_if_asked

DOMAIN = '@google.com'
SAMPLE_MX = 'sample.aspmx.l.google.com'
ATOM_STR = string.ascii_letters + string.digits + '!#$%&\'*+-/=?^_`{|}~'

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

    # very simple test that should fail Google Apps custom grammar
    addr_string = '!mailgun' + DOMAIN
    addr = address.validate_address(addr_string)
    assert_equal(addr, None)


def test_google_pass():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # if single character, must be alphanum, underscore, or apostrophe
        for i in string.ascii_letters + string.digits + '_\'':
            localpart = str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # valid length range
        for i in range(1, 65):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # start must be alphanum, underscore, dash, or apostrophe
        for i in string.ascii_letters + string.digits + '_-\'':
            localpart = str(i) + 'aaaaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # end must be alphanum, underscore, dash, or apostrophe
        for i in string.ascii_letters + string.digits + '_-\'':
            localpart = 'aaaaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # must be alphanum, underscore, dash, apostrophe, dots
        for i in string.ascii_letters + string.digits + '_-\'.':
            localpart = 'aaa' + str(i) + '000'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # everything after plus (+) is ignored
        for localpart in ['aa+', 'aa+tag', 'aa+tag+tag', 'aa++tag', 'aa+' + ATOM_STR]:
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)


def test_google_fail():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # invalid single character (must be alphanum, underscore, or apostrophe)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('_', '')
        invalid_chars = invalid_chars.replace('\'', '')
        for i in invalid_chars:
            localpart = str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid length range
        for i in range(0) + range(65, 80):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid start char (must start with alphanum, underscore, dash, or apostrophe)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('_', '')
        invalid_chars = invalid_chars.replace('-', '')
        invalid_chars = invalid_chars.replace('\'', '')
        for i in invalid_chars:
            localpart = str(i) + 'aaaaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid end char (must end with alphanum, underscore, dash, or apostrophe)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('_', '')
        invalid_chars = invalid_chars.replace('-', '')
        invalid_chars = invalid_chars.replace('\'', '')
        invalid_chars = invalid_chars.replace('+', '')
        for i in invalid_chars:
            localpart = 'aaaaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid chars (must be alphanum, underscore, dash, apostrophe, dots)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('_', '')
        invalid_chars = invalid_chars.replace('-', '')
        invalid_chars = invalid_chars.replace('\'', '')
        invalid_chars = invalid_chars.replace('.', '')
        invalid_chars = invalid_chars.replace('+', '')
        for i in invalid_chars:
            localpart = 'aaa' + str(i) + '000'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # dots (.) are NOT ignored
        addr1 = address.validate_address('aa..aa' + DOMAIN)
        addr2 = address.validate_address('aa.aa' + DOMAIN)
        assert_not_equal(addr1, addr2)

        # everything after plus (+) is ignored, but something must be infront of it
        for localpart in ['+t1', '+' + ATOM_STR]:
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)
