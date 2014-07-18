# coding:utf-8

import email
from cStringIO import StringIO
from contextlib import closing
from email import message_from_string

from nose.tools import ok_, eq_, assert_false

from flanker.mime.message.fallback import create
from flanker.mime import recover
from tests import (IPHONE, ENCLOSED, TORTURE, TEXT_ONLY, MAILFORMED_HEADERS,
                   SPAM_BROKEN_HEADERS, BILINGUAL, MULTI_RECEIVED_HEADERS,
                   MAILGUN_PIC, BOUNCE)


def bad_string_test():
    mime = "Content-Type: multipart/broken\n\n"
    message = create.from_string("Content-Type:multipart/broken")
    eq_(mime, message.to_string())
    with closing(StringIO()) as out:
        message.to_stream(out)
        eq_(mime, out.getvalue())
    list(message.walk())
    message.remove_headers()
    assert_false(message.is_attachment())
    assert_false(message.is_inline())
    assert_false(message.is_delivery_notification())
    assert_false(message.is_bounce())
    ok_(message.to_python_message())
    eq_(None, message.get_attached_message())
    ok_(str(message))


def bad_string_test_2():
    mime = "Content-Mype: multipart/broken\n\n"
    message = create.from_string(mime)
    ok_(message.content_type)
    eq_((None, {}), message.content_disposition)


def bad_python_test():
    message = create.from_python(
        message_from_string("Content-Type:multipart/broken"))
    ok_(message.to_string())
    with closing(StringIO()) as out:
        message.to_stream(out)
        ok_(out.getvalue())
    list(message.walk())
    message.remove_headers()
    assert_false(message.is_attachment())
    assert_false(message.is_inline())
    assert_false(message.is_delivery_notification())
    assert_false(message.is_bounce())
    ok_(message.to_python_message())
    eq_(None, message.get_attached_message())
    ok_(str(message))


def message_alter_body_and_serialize_test():
    message = create.from_string(IPHONE)

    parts = list(message.walk())
    eq_(3, len(parts))
    eq_(u'\n\n\n~Danielle', parts[2].body)
    eq_((None, {}), parts[2].content_disposition)
    eq_(('inline', {'filename': 'photo.JPG'}), parts[1].content_disposition)

    part = list(message.walk())[2]
    part.body = u'Привет, Danielle!\n\n'

    with closing(StringIO()) as out:
        message.to_stream(out)
        message1 = create.from_string(out.getvalue())
        message2 = create.from_string(message.to_string())

    parts = list(message1.walk())
    eq_(3, len(parts))
    eq_(u'Привет, Danielle!\n\n', parts[2].body)

    parts = list(message2.walk())
    eq_(3, len(parts))
    eq_(u'Привет, Danielle!\n\n', parts[2].body)


def message_content_dispositions_test():
    message = create.from_string(IPHONE)

    parts = list(message.walk())
    eq_((None, {}), parts[2].content_disposition)
    eq_(('inline', {'filename': 'photo.JPG'}), parts[1].content_disposition)

    message = create.from_string("Content-Disposition: Нельзя распарсить")
    parts = list(message.walk(with_self=True))
    eq_((None, {}), parts[0].content_disposition)


def message_from_python_test():
    message = create.from_string(ENCLOSED)
    eq_(2, len(message.parts))
    eq_('multipart/alternative', message.parts[1].enclosed.content_type)
    eq_('multipart/mixed', message.content_type)
    assert_false(message.body)

    message.headers['Sasha'] = 'Hello!'
    message.parts[1].enclosed.headers['Yo'] = u'Man'
    ok_(message.to_string())
    ok_(str(message))
    ok_(str(message.parts[0]))
    eq_('4FEEF9B3.7060508@example.net', message.message_id)
    eq_('Wow', message.subject)

    m = message.get_attached_message()
    eq_('multipart/alternative', str(m.content_type))
    eq_('Thanks!', m.subject)


def set_message_id_test():
    # Given
    message = create.from_string(ENCLOSED)

    # When
    message.message_id = 'some.message.id@example.net'

    # Then
    eq_('some.message.id@example.net', message.message_id)
    eq_('<some.message.id@example.net>', message.headers['Message-Id'])


def clean_subject_test():
    # Given
    message = create.from_string(ENCLOSED)
    message.headers['Subject'] = 'FWD: RE: FW: Foo Bar'

    # When/Then
    eq_('Foo Bar', message.clean_subject)


def references_test():
    # Given
    message = create.from_python(
        email.message_from_string(MULTI_RECEIVED_HEADERS))

    # When/Then
    eq_({'AANLkTi=1ANR2FzeeQ-vK3-_ty0gUrOsAxMRYkob6CL-c@mail.gmail.com',
         'AANLkTinUdYK2NpEiYCKGnCEp_OXKqst_bWNdBVHsfDVh@mail.gmail.com'},
        set(message.references))


def detected_fields_test():
    # Given
    message = create.from_string(MAILGUN_PIC)
    attachment = message.parts[1]

    # When/Then
    eq_('mailgun.png', attachment.detected_file_name)
    eq_('png', attachment.detected_subtype)
    eq_('image', attachment.detected_format)
    ok_(not attachment.is_body())


def bounce_test():
    # When
    message = create.from_string(BOUNCE)

    # Then
    ok_(message.is_bounce())
    eq_('5.1.1', message.bounce.status)
    eq_('smtp; 550-5.1.1 The email account that you tried to reach does '
        'not exist. Please try 550-5.1.1 double-checking the recipient\'s email '
        'address for typos or 550-5.1.1 unnecessary spaces. Learn more at '
        '550 5.1.1 http://mail.google.com/support/bin/answer.py?answer=6596 '
        '17si20661415yxe.22',
        message.bounce.diagnostic_code)


def torture_test():
    message = create.from_string(TORTURE)
    ok_(list(message.walk(with_self=True)))
    ok_(message.size)
    message.parts[0].content_encoding = 'blablac'


def text_only_test():
    message = create.from_string(TEXT_ONLY)
    eq_(u"Hello,\nI'm just testing message parsing\n\nBR,\nBob",
        message.body)
    ok_(not message.is_bounce())
    eq_(None, message.get_attached_message())


def message_headers_test():
    message = create.from_python(email.message_from_string(ENCLOSED))

    ok_(message.headers)
    eq_(20, len(message.headers))

    # iterate a little bit
    for key, val in message.headers:
        ok_(key)
        ok_(val)

    for key, val in message.headers.items():
        ok_(key)
        ok_(val)

    for key, val in message.headers.iteritems():
        ok_(key)
        ok_(val)

    message.headers.prepend("Received", "Hi")
    message.headers.add("Received", "Yo")
    eq_(22, len(message.headers.keys()))
    ok_(message.headers.get("Received"))
    ok_(message.headers.getall("Received"))
    eq_("a", message.headers.get("Received-No", "a"))
    ok_(str(message.headers))


def bilingual_test():
    message = create.from_string(BILINGUAL)
    eq_(u"Simple text. How are you? Как ты поживаешь?",
        message.headers['Subject'])

    for key, val in message.headers:
        if key == 'Subject':
            eq_(u"Simple text. How are you? Как ты поживаешь?", val)

    message.headers['Subject'] = u"Да все ок!"
    eq_(u"Да все ок!", message.headers['Subject'])

    message = create.from_string(message.to_string())
    eq_(u"Да все ок!", message.headers['Subject'])

    eq_("", message.headers.get("SashaNotExists", ""))


def broken_headers_test():
    message = create.from_string(MAILFORMED_HEADERS)
    ok_(message.headers['Subject'])
    eq_(unicode, type(message.headers['Subject']))


def broken_headers_test_2():
    message = create.from_string(SPAM_BROKEN_HEADERS)
    ok_(message.headers['Subject'])
    eq_(unicode, type(message.headers['Subject']))
    eq_(('text/plain', {'charset': 'iso-8859-1'}),
        message.headers['Content-Type'])
    eq_(unicode, type(message.body))


def test_walk():
    message = recover(ENCLOSED)
    expected = [
        'multipart/mixed',
        'text/plain',
        'message/rfc822',
        'multipart/alternative',
        'text/plain',
        'text/html'
        ]
    eq_(expected[1:], [str(p.content_type) for p in message.walk()])
    eq_(expected, [str(p.content_type) for p in message.walk(with_self=True)])
    eq_(['text/plain', 'message/rfc822'],
        [str(p.content_type) for p in message.walk(skip_enclosed=True)])
