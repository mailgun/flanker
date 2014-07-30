# coding:utf-8

from email.header import Header

from nose.tools import eq_, ok_
from mock import patch, Mock

from flanker.mime.message import headers
from flanker.mime.message.headers.encoding import (encode_unstructured,
                                                   encode_string)
from flanker.mime.message import part
from flanker.mime import create
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
                "\n 75,250,234 times!")
    eq_(folded_s, headers.to_mime('Subject', s))


def string_maxlinelen_test():
    """
    If the encoded string is longer then the maximum line length, which is 76,
    by default then it is broken down into lines. But a maximum line length
    value can be provided in the `maxlinelen` parameter.
    """
    eq_("very\n loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong",
        encode_string(None, "very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong"))

    eq_("very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong",
        encode_string(None, "very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong", maxlinelen=78))


@patch.object(part.MimePart, 'was_changed', Mock(return_value=True))        
def max_header_length_test():
    message = create.from_string(LONG_HEADER)

    # this used to fail because exceeded max depth recursion
    ok_(message.headers.getraw('subject').encode("utf-8") in message.to_string())

    unicode_subject = (u"Это сообщение с длинным сабжектом "
                       u"специально чтобы проверить кодировки")
    ascii_subject = "This is simple ascii subject"

    with patch.object(
        headers.encoding, 'MAX_HEADER_LENGTH', len(ascii_subject) + 1):

        eq_(Header(ascii_subject.encode("ascii"), "ascii", header_name="Subject"),
            encode_unstructured("Subject", ascii_subject))

    with patch.object(
        headers.encoding, 'MAX_HEADER_LENGTH', len(unicode_subject) + 1):

        eq_(Header(unicode_subject.encode("utf-8"), "utf-8", header_name="Subject"),
            encode_unstructured("Subject", unicode_subject))

    with patch.object(headers.encoding, 'MAX_HEADER_LENGTH', 1):

        eq_(ascii_subject.encode("utf-8"),
            encode_unstructured("Subject", ascii_subject))

        eq_(unicode_subject.encode("utf-8"),
            encode_unstructured("Subject", unicode_subject))

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
