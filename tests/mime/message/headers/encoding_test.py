# coding:utf-8

from mock import patch, Mock
from nose.tools import eq_, ok_

from flanker.mime import create
from flanker.mime.message import headers, part
from flanker.mime.message.headers.encoding import _encode_unstructured
from tests import LONG_HEADER, ENCODED_HEADER


def encodings_test():
    s = (u"Это сообщение с длинным сабжектом "
         u"специально чтобы проверить кодировки")

    eq_(s, headers.mime_to_unicode(headers.to_mime('Subject', s)))

    s = "this is sample ascii string"

    eq_(s, headers.to_mime('Subject',s))
    eq_(s, headers.mime_to_unicode(s))

    s = ("This is a long subject with commas, bob, Jay, suzy, tom, over"
         " 75,250,234 times!")
    folded_s = ("This is a long subject with commas, bob, Jay, suzy, tom, over"
                "\r\n 75,250,234 times!")
    eq_(folded_s, headers.to_mime('Subject', s))


def encode_address_test():
    eq_('john.smith@example.com', headers.to_mime('To', 'john.smith@example.com'))
    eq_('"John Smith" <john.smith@example.com>', headers.to_mime('To', '"John Smith" <john.smith@example.com>'))
    eq_('Федот <стрелец@письмо.рф>', headers.to_mime('To', 'Федот <стрелец@письмо.рф>'))
    eq_('=?utf-8?b?0KTQtdC00L7Rgg==?= <foo@xn--h1aigbl0e.xn--p1ai>', headers.to_mime('To', 'Федот <foo@письмо.рф>'))


@patch.object(part.MimePart, 'was_changed', Mock(return_value=True))        
def max_header_length_test():
    message = create.from_string(LONG_HEADER)

    # this used to fail because exceeded max depth recursion
    message.to_string()

    ascii_subject = 'This is simple ascii subject'
    eq_('This is simple ascii subject',
        _encode_unstructured('Subject', ascii_subject))

    unicode_subject = (u'Это сообщение с длинным сабжектом '
                       u'специально чтобы проверить кодировки')
    eq_('=?utf-8?b?0K3RgtC+INGB0L7QvtCx0YnQtdC90LjQtSDRgSDQtNC70LjQvdC9?=\r\n'
        ' =?utf-8?b?0YvQvCDRgdCw0LHQttC10LrRgtC+0Lwg0YHQv9C10YbQuNCw0LvRjNC90L4g?=\r\n'
        ' =?utf-8?b?0YfRgtC+0LHRiyDQv9GA0L7QstC10YDQuNGC0Ywg0LrQvtC00LjRgNC+0LI=?=\r\n'
        ' =?utf-8?b?0LrQuA==?=',
        _encode_unstructured('Subject', unicode_subject))


def add_header_preserve_original_encoding_test():
    message = create.from_string(ENCODED_HEADER)

    # save original encoded from header
    original_from = message.headers.getraw('from')

    # check if the raw header was not decoded
    ok_('=?UTF-8?B?Rm9vLCBCYXI=?=' in original_from)

    # add a header
    message.headers.add('foo', 'bar')

    # check original encoded header is still in the mime string
    ok_(original_from in message.to_string())
