# coding:utf-8

import json
from email.parser import Parser

from nose.tools import *

from flanker import _email
from flanker.mime import create
from flanker.mime.message import errors
from flanker.mime.message.part import MimePart
from ... import *


def from_python_message_test():
    python_message = Parser().parsestr(MULTIPART)
    message = create.from_python(python_message)

    eq_(python_message['Subject'], message.headers['Subject'])

    ctypes = [p.get_content_type() for p in python_message.walk()]
    ctypes2 = [str(p.content_type) for p in message.walk(with_self=True)]
    eq_(ctypes, ctypes2)

    payloads = [p.get_payload(decode=True) for p in python_message.walk()][1:]
    payloads2 = [p.body for p in message.walk()]

    eq_(3, len(payloads2))
    eq_(payloads[0].decode('utf-8'), payloads2[0])
    eq_(payloads[1], payloads2[1])
    eq_(payloads[2].decode('utf-8'), payloads2[2])


def from_string_message_test():
    message = create.from_string(IPHONE)
    parts = list(message.walk())
    eq_(3, len(parts))
    eq_(u'\r\n\r\n\r\n~Danielle', parts[2].body)


def from_part_message_simple_test():
    message = create.from_string(IPHONE)
    parts = list(message.walk())

    message = create.from_message(parts[2])
    eq_(u'\r\n\r\n\r\n~Danielle', message.body)


def message_from_garbage_test():
    assert_raises(errors.DecodingError, create.from_string, None)
    assert_raises(errors.DecodingError, create.from_string, [])
    assert_raises(errors.DecodingError, create.from_string, MimePart)


def create_singlepart_ascii_test():
    message = create.text("plain", u"Hello")
    message = create.from_string(message.to_string())
    eq_("7bit", message.content_encoding.value)
    eq_("Hello", message.body)


def create_singlepart_unicode_qp_test():
    message = create.text("plain", u"Привет, курилка")
    message = create.from_string(message.to_string())
    eq_("quoted-printable", message.content_encoding.value)
    eq_(u"Привет, курилка", message.body)


def create_singlepart_ascii_long_lines_test():
    very_long = "very long line  " * 1000 + "preserve my newlines \r\n\r\n"
    message = create.text("plain", very_long)

    message2 = create.from_string(message.to_string())
    eq_("quoted-printable", message2.content_encoding.value)
    eq_(very_long, message2.body)

    message2 = _email.message_from_string(message.to_string())
    eq_(very_long, message2.get_payload(decode=True).decode('utf-8'))


def create_multipart_simple_test():
    message = create.multipart("mixed")
    message.append(
        create.text("plain", "Hello"),
        create.text("html", "<html>Hello</html>"))
    ok_(message.is_root())
    assert_false(message.parts[0].is_root())
    assert_false(message.parts[1].is_root())

    message2 = create.from_string(message.to_string())
    eq_(2, len(message2.parts))
    eq_("multipart/mixed", message2.content_type)
    eq_(2, len(message.parts))
    eq_("Hello", message.parts[0].body)
    eq_("<html>Hello</html>", message.parts[1].body)

    message2 = _email.message_from_string(message.to_string())
    eq_("multipart/mixed", message2.get_content_type())
    eq_("Hello", message2.get_payload()[0].get_payload(decode=False))
    eq_("<html>Hello</html>",
        message2.get_payload()[1].get_payload(decode=False))


def create_multipart_with_attachment_test():
    message = create.multipart("mixed")
    filename = u"Мейлган картиночка картиночечка с длинным  именем и пробельчиками"
    message.append(
        create.text("plain", "Hello"),
        create.text("html", "<html>Hello</html>"),
        create.binary(
            "image", "png", MAILGUN_PNG,
            filename, "attachment"))
    eq_(3, len(message.parts))

    message2 = create.from_string(message.to_string())
    eq_(3, len(message2.parts))
    eq_("base64", message2.parts[2].content_encoding.value)
    eq_(MAILGUN_PNG, message2.parts[2].body)
    eq_(filename, message2.parts[2].content_disposition.params['filename'])
    eq_(filename, message2.parts[2].content_type.params['name'])
    ok_(message2.parts[2].is_attachment())

    message2 = _email.message_from_string(message.to_string())
    eq_(3, len(message2.get_payload()))
    eq_(MAILGUN_PNG, message2.get_payload()[2].get_payload(decode=True))


def create_multipart_with_text_non_unicode_attachment_test():
    """
    Make sure we encode text attachment in base64
    """
    message = create.multipart("mixed")
    filename = "text-attachment.txt"
    message.append(
        create.text("plain", "Hello"),
        create.text("html", "<html>Hello</html>"),
        create.binary(
            "text", "plain", u"Саша с уралмаша".encode("koi8-r"),
            filename, "attachment"))

    message2 = create.from_string(message.to_string())

    eq_(3, len(message2.parts))
    attachment = message2.parts[2]
    ok_(attachment.is_attachment())
    eq_("base64", attachment.content_encoding.value)
    eq_(u"Саша с уралмаша", attachment.body)


def create_multipart_with_text_non_unicode_attachment_preserve_encoding_test():
    """Make sure we encode text attachment in base64
    and also preserve charset information
    """
    message = create.multipart("mixed")
    filename = "text-attachment.txt"
    message.append(
        create.text("plain", "Hello"),
        create.text("html", "<html>Hello</html>"),
        create.text(
            "plain",
            u"Саша с уралмаша 2".encode("koi8-r"),
            "koi8-r",
            "attachment",
            filename))

    message2 = create.from_string(message.to_string())

    eq_(3, len(message2.parts))
    attachment = message2.parts[2]
    ok_(attachment.is_attachment())
    eq_("base64", attachment.content_encoding.value)
    eq_("koi8-r", attachment.charset)
    eq_(u"Саша с уралмаша 2", attachment.body)


def create_multipart_nested_test():
    message = create.multipart("mixed")
    nested = create.multipart("alternative")
    nested.append(
        create.text("plain", u"Саша с уралмаша"),
        create.text("html", u"<html>Саша с уралмаша</html>"))
    message.append(
        create.text("plain", "Hello"),
        nested)

    message2 = create.from_string(message.to_string())
    eq_(2, len(message2.parts))
    eq_('text/plain', message2.parts[0].content_type)
    eq_('Hello', message2.parts[0].body)

    eq_(u"Саша с уралмаша", message2.parts[1].parts[0].body)
    eq_(u"<html>Саша с уралмаша</html>", message2.parts[1].parts[1].body)

def create_bounced_email_test():
    google_delivery_failed = """Delivered-To: user@gmail.com
Content-Type: multipart/report; boundary=f403045f50f42d03f10546f0cb14; report-type=delivery-status

--f403045f50f42d03f10546f0cb14
Content-Type: message/delivery-status

--f403045f50f42d03f10546f0cb14
Content-Type: message/rfc822

MIME-Version: 1.0
From: Test <test@test.com>
To: fake@faketestemail.xxx
Content-Type: multipart/alternative; boundary=f403045f50f42690580546f0cb4d

There should be a boundary here!

--f403045f50f42d03f10546f0cb14--
"""

    message = create.from_string(google_delivery_failed)
    eq_(google_delivery_failed, message.to_string())
    eq_(None, message.get_attached_message())

def create_bounced_email_attached_message_test():
    attached_message = """MIME-Version: 1.0
From: Test <test@test.com>
To: fake@faketestemail.xxx
Content-Type: multipart/alternative; boundary=f403045f50f42690580546f0cb4d

--f403045f50f42690580546f0cb4d
Content-Type: text/plain
Content-Transfer-Encoding: 8bit

how are you?

--f403045f50f42690580546f0cb4d--
"""
    google_delivery_failed = """Delivered-To: user@gmail.com
Content-Type: multipart/report; boundary=f403045f50f42d03f10546f0cb14; report-type=delivery-status

--f403045f50f42d03f10546f0cb14
Content-Type: message/delivery-status

--f403045f50f42d03f10546f0cb14
Content-Type: message/rfc822

{msg}
--f403045f50f42d03f10546f0cb14--
""".format(msg=attached_message)

    message = create.from_string(google_delivery_failed)
    eq_(google_delivery_failed, message.to_string())
    eq_(attached_message, message.get_attached_message().to_string())


def create_enclosed_test():
    message = create.text("plain", u"Превед")
    message.headers['From'] = u' Саша <sasha@mailgun.net>'
    message.headers['To'] = u'Женя <ev@mailgun.net>'
    message.headers['Subject'] = u"Все ли ок? Нормальненько??"

    message = create.message_container(message)

    message2 = create.from_string(message.to_string())
    eq_('message/rfc822', message2.content_type)
    eq_(u"Превед", message2.enclosed.body)
    eq_(u'Саша <sasha@mailgun.net>', message2.enclosed.headers['From'])


def create_enclosed_nested_test():
    nested = create.multipart("alternative")
    nested.append(
        create.text("plain", u"Саша с уралмаша"),
        create.text("html", u"<html>Саша с уралмаша</html>"))

    message = create.multipart("mailgun-recipient-variables")
    variables = {"a": u"<b>Саша</b>" * 1024}
    message.append(
        create.binary("application", "json", json.dumps(variables)),
        create.message_container(nested))

    message2 = create.from_string(message.to_string())
    eq_(variables, json.loads(message2.parts[0].body))

    nested = message2.parts[1].enclosed
    eq_(2, len(nested.parts))
    eq_(u"Саша с уралмаша", nested.parts[0].body)
    eq_(u"<html>Саша с уралмаша</html>", nested.parts[1].body)


def guessing_attachments_test():
    binary = create.binary('application', 'octet-stream', MAILGUN_PNG,
                           '/home/alex/mailgun.png')
    eq_('image/png', binary.content_type)
    eq_('mailgun.png', binary.content_type.params['name'])

    binary = create.binary('application', 'octet-stream', MAILGUN_PIC,
                           '/home/alex/mailgun.png', disposition='attachment')

    eq_('attachment', binary.headers['Content-Disposition'].value)
    eq_('mailgun.png', binary.headers['Content-Disposition'].params['filename'])

    binary = create.binary('application', 'octet-stream', NOTIFICATION,
                           '/home/alex/mailgun.eml')
    eq_('message/rfc822', binary.content_type)

    binary = create.binary('application', 'octet-stream', MAILGUN_WAV,
                           '/home/alex/audiofile.wav')
    eq_('audio/x-wav', binary.content_type)


def attaching_emails_test():
    attachment = create.attachment(
        "message/rfc822", MULTIPART, "message.eml", "attachment")
    eq_("message/rfc822", attachment.content_type)
    ok_(attachment.is_attachment())

    # now guess by file name
    attachment = create.attachment(
        "application/octet-stream", MULTIPART, "message.eml", "attachment")
    eq_("message/rfc822", attachment.content_type)


def attaching_broken_emails_test():
    attachment = create.attachment(
        "application/octet-stream", FALSE_MULTIPART, "message.eml", "attachment")
    ok_(attachment.is_attachment())
    eq_("application/octet-stream", attachment.content_type)


def attaching_images_test():
    attachment = create.attachment(
        "application/octet-stream", MAILGUN_PNG, "/home/alex/mailgun.png")
    eq_("image/png", attachment.content_type)


def attaching_text_test():
    attachment = create.attachment(
        "application/octet-stream",
        u"Привет, как дела".encode("koi8-r"), "/home/alex/hi.txt")
    eq_("text/plain", attachment.content_type)
    eq_(u"Привет, как дела", attachment.body)


def guessing_text_encoding_test():
    text = create.text("plain", "hello", "utf-8")
    eq_('ascii', text.charset)

    text = create.text("plain", u"hola, привет", "utf-8")
    eq_('utf-8', text.charset)


def create_long_lines_test():
    val = "hello" * 1024
    text = create.text("plain", val, "utf-8")
    eq_('ascii', text.charset)

    create.from_string(text.to_string())
    eq_(val, text.body)


def create_newlines_in_headers_test():
    text = create.text("plain", 'yo', "utf-8")
    text.headers['Subject'] = 'Hello,\nnewline\r\n\r\n'
    text.headers.add('To', u'\n\nПревед, медвед\n!\r\n')

    text = create.from_string(text.to_string())
    eq_('Hello,newline', text.headers['Subject'])
    eq_(u'Превед, медвед!', text.headers['To'])


def test_bug_line_is_too_long():
    # It was possible to create a message with a very long header value, but
    # it was impossible to parse such message.

    msg = create.text('plain', 'foo', 'utf-8')
    msg.headers.add('bar', 'y' * 10000)
    encoded_msg = msg.to_string()
    decoded_msg = create.from_string(encoded_msg)

    # When/Then
    decoded_msg.headers
