# coding:utf-8

import email.header

from flanker.addresslib.address import is_email
from flanker.mime.message.headers.encodedword import mime_to_unicode
from mock import patch, Mock
from nose.tools import assert_equal, assert_not_equal
from nose.tools import assert_true, assert_false


def test_is_email():
    assert_true(is_email("ev@host"))
    assert_true(is_email("ev@host.com.com.com"))

    assert_false(is_email("evm"))
    assert_false(is_email(None))


def test_header_to_unicode():
    assert_equal(u'Eugueny ώ Kontsevoy', mime_to_unicode("=?UTF-8?Q?Eugueny_=CF=8E_Kontsevoy?=") )
    assert_equal(u'hello', mime_to_unicode("hello"))
    assert_equal(None, mime_to_unicode(None))
