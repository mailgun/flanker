# coding:utf-8

from email.header import Header

from nose.tools import *
from mock import *

from flanker.mime.message import headers
from flanker.mime.message.headers.encoding import encode_unstructured
from flanker.mime.message import part
from flanker.mime.message.part import MimePart
from flanker.mime import create
from .... import LONG_HEADER


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


@patch.object(part.MimePart, 'was_changed', Mock(return_value=True))        
def max_header_length_test():
    message = create.from_string(LONG_HEADER)
    # this used to fail because exceeded max depth recursion
    ok_(message.headers["Subject"].encode("utf-8") in message.to_string())

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
