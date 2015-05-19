# coding:utf-8

import random
import string

from flanker.addresslib import address
from flanker.addresslib import validate

from mock import patch
from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from ... import skip_if_asked

DOMAIN = '@gmail.com'
SAMPLE_MX = 'sample.gmail-smtp-in.l.google.com'
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

    # very simple test that should fail Gmail custom grammar
    addr_string = '!mailgun' + DOMAIN
    addr = address.validate_address(addr_string)
    assert_equal(addr, None)


def test_gmail_pass():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # valid length range
        for i in range(6, 31):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # start must be letter or num
        for i in string.ascii_letters + string.digits:
            localpart = str(i) + 'aaaaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # end must be letter or number
        for i in string.ascii_letters + string.digits:
            localpart = 'aaaaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # must be letter, num, or dots
        for i in string.ascii_letters + string.digits + '.':
            localpart = 'aaa' + str(i) + '000'
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # non-consecutive dots (.) within an address are legal
        for localpart in ['a.aaaaa', 'aa.aaaa', 'aaa.aaa','aa.aa.aa']:
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)

        # everything after plus (+) is ignored
        for localpart in ['aaaaaa+', 'aaaaaa+tag', 'aaaaaa+tag+tag','aaaaaa++tag', 'aaaaaa+' + ATOM_STR]:
            addr = address.validate_address(localpart + DOMAIN)
            assert_not_equal(addr, None)


def test_gmail_fail():
    with patch.object(validate, 'mail_exchanger_lookup') as mock_method:
        mock_method.side_effect = mock_exchanger_lookup

        # invalid length range
        for i in range(0, 6) + range(31, 40):
            localpart = ''.join(random.choice(string.ascii_letters) for x in range(i))
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid start char (must start with letter)
        for i in string.punctuation:
            localpart = str(i) + 'aaaaa'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid end char (must end with letter or digit)
        for i in string.punctuation:
            localpart = 'aaaaa' + str(i)
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid chars (must be letter, num, or dot)
        invalid_chars = string.punctuation
        invalid_chars = invalid_chars.replace('.', '')
        for i in invalid_chars:
            localpart = 'aaa' + str(i) + '000'
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # invalid consecutive dots (.)
        for localpart in ['aaaaaa......', '......aaaaaa', 'aaa......aaa','aa...aa...aa']:
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)

        # everything after plus (+) is ignored
        for localpart in ['+t1', 'a+t1', 'aa+', 'aaa+t1', 'aaaa+t1+t2','aaaaa++t1']:
            addr = address.validate_address(localpart + DOMAIN)
            assert_equal(addr, None)
