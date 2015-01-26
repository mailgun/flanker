# coding:utf-8
from email import message_from_string
from contextlib import closing
from cStringIO import StringIO

from nose.tools import eq_, ok_, assert_false, assert_raises, assert_less

from flanker.mime.create import multipart, text
from flanker.mime.message.scanner import scan
from flanker.mime.message.errors import EncodingError, DecodingError
from flanker.mime.message.part import encode_transfer_encoding
from tests import (BILINGUAL, BZ2_ATTACHMENT, ENCLOSED, TORTURE, TORTURE_PART,
                   ENCLOSED_BROKEN_ENCODING, EIGHT_BIT, QUOTED_PRINTABLE,
                   TEXT_ONLY, ENCLOSED_BROKEN_BODY, RUSSIAN_ATTACH_YAHOO,
                   MAILGUN_PIC, MAILGUN_PNG, MULTIPART, IPHONE,
                   SPAM_BROKEN_CTYPE, BOUNCE, NDN, NO_CTYPE, RELATIVE,
                   MULTI_RECEIVED_HEADERS)
from tests.mime.message.scanner_test import TORTURE_PARTS, tree_to_string


def readonly_immutability_test():
    """We can read the headers and access the body without changing a single
    char inside the message"""

    message = scan(BILINGUAL)
    eq_(u"Simple text. How are you? Как ты поживаешь?",
        message.headers['Subject'])
    assert_false(message.was_changed())
    eq_(BILINGUAL, message.to_string())

    message = scan(ENCLOSED)
    pmessage = message_from_string(ENCLOSED)

    # we can read the headers without changing anything
    eq_(u'"Александр Клижентас☯" <bob@example.com>',
        message.headers['To'])
    eq_('Bob Marley <bob@example.net>, Jimmy Hendrix <jimmy@examplehq.com>',
        message.parts[1].enclosed.headers['To'])
    assert_false(message.was_changed())

    # we can also read the body without changing anything
    pbody = pmessage.get_payload()[1].get_payload()[0].get_payload()[0].get_payload(decode=True)
    pbody = unicode(pbody, 'utf-8')
    eq_(pbody, message.parts[1].enclosed.parts[0].body)
    assert_false(message.was_changed())
    eq_(ENCLOSED, message.to_string())


def top_level_headers_immutability_test():
    """We can change the headers without changing the body"""
    message = scan(ENCLOSED)
    message.headers['Subject'] = u'☯Привет! Как дела? Что делаешь?☯'
    out = message.to_string()
    a = ENCLOSED.split("--===============6195527458677812340==", 1)[1]
    b = out.split("--===============6195527458677812340==", 1)[1]
    eq_(a, b, "Bodies should not be changed in any way")


def immutability_test():
    """We can read the headers without changing a single
    char inside the message"""
    message = scan(BILINGUAL)
    eq_(u"Simple text. How are you? Как ты поживаешь?",
        message.headers['Subject'])
    eq_(BILINGUAL, message.to_string())

    message = scan(TORTURE)
    eq_('Multi-media mail demonstration ', message.headers['Subject'])
    eq_(TORTURE, message.to_string())

    message = scan(TORTURE)
    eq_('Multi-media mail demonstration ', message.headers['Subject'])
    with closing(StringIO()) as out:
        message.to_stream(out)
        eq_(TORTURE.rstrip(), out.getvalue().rstrip())


def enclosed_first_part_alternation_test():
    """We've changed one part of the message only, the rest was not changed"""
    message = scan(ENCLOSED)
    message.parts[0].body = 'Hey!\n'
    out = message.to_string()

    a = ENCLOSED.split("--===============6195527458677812340==", 2)[2]
    b = out.split("--===============6195527458677812340==", 2)[2]
    eq_(a, b, "Enclosed message should not be changed")

    message2 = scan(out)
    eq_('Hey!\n', message2.parts[0].body)
    eq_(message.parts[1].enclosed.parts[1].body,
        message2.parts[1].enclosed.parts[1].body)


def enclosed_header_alternation_test():
    """We've changed the headers in the inner part of the message only,
    the rest was not changed"""
    message = scan(ENCLOSED)

    enclosed = message.parts[1].enclosed
    enclosed.headers['Subject'] = u'☯Привет! Как дела? Что делаешь?☯'
    out = message.to_string()

    a = ENCLOSED.split("--===============4360815924781479146==", 1)[1]
    a = a.split("--===============4360815924781479146==--")[0]

    b = out.split("--===============4360815924781479146==", 1)[1]
    b = b.split("--===============4360815924781479146==--")[0]
    eq_(a, b)


def enclosed_header_inner_alternation_test():
    """We've changed the headers in the inner part of the message only,
    the rest was not changed"""
    message = scan(ENCLOSED)

    unicode_value = u'☯Привет! Как дела? Что делаешь?☯'
    enclosed = message.parts[1].enclosed
    enclosed.parts[0].headers['Subject'] = unicode_value

    message2 = scan(message.to_string())
    enclosed2 = message2.parts[1].enclosed

    eq_(unicode_value, enclosed2.parts[0].headers['Subject'])
    eq_(enclosed.parts[0].body, enclosed2.parts[0].body)
    eq_(enclosed.parts[1].body, enclosed2.parts[1].body)



def enclosed_body_alternation_test():
    """We've changed the body in the inner part of the message only,
    the rest was not changed"""
    message = scan(ENCLOSED)

    value = u'☯Привет! Как дела? Что делаешь?, \r\n\r Что новенького?☯'
    enclosed = message.parts[1].enclosed
    enclosed.parts[0].body = value
    out = message.to_string()

    message = scan(out)
    enclosed = message.parts[1].enclosed
    eq_(value, enclosed.parts[0].body)


def enclosed_inner_part_no_headers_test():
    """We've changed the inner part of the entity that has no headers,
    make sure that it was processed correctly"""
    message = scan(TORTURE_PART)

    enclosed = message.parts[1].enclosed
    no_headers = enclosed.parts[0]
    assert_false(no_headers.headers)
    no_headers.body = no_headers.body + "Mailgun!"

    message = scan(message.to_string())
    enclosed = message.parts[1].enclosed
    no_headers = enclosed.parts[0]
    ok_(no_headers.body.endswith("Mailgun!"))


def enclosed_broken_encoding_test():
    """ Make sure we can serialize the message even in case of Decoding errors,
    in this case fallback happens"""

    message = scan(ENCLOSED_BROKEN_ENCODING)
    for p in message.walk():
        try:
            p.headers['A'] = 'b'
        except:
            pass
    with closing(StringIO()) as out:
        message.to_stream(out)
        ok_(out.getvalue())



def double_serialization_test():
    message = scan(TORTURE)
    message.headers['Subject'] = u'Поменяли текст ☢'

    a = message.to_string()
    b = message.to_string()
    with closing(StringIO()) as out:
        message.to_stream(out)
        c = out.getvalue()
    eq_(a, b)
    eq_(b, c)


def preserve_content_encoding_test_8bit():
    """ Make sure that content encoding will be preserved if possible"""
    # 8bit messages
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'

    # should remain 8bit
    message = scan(EIGHT_BIT)
    message.parts[0].body = unicode_value

    message = scan(message.to_string())
    eq_(unicode_value, message.parts[0].body)
    eq_('8bit', message.parts[0].content_encoding.value)


def preserve_content_encoding_test_quoted_printable():
    """ Make sure that quoted-printable remains quoted-printable"""
    # should remain 8bit
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'
    message = scan(QUOTED_PRINTABLE)
    body = message.parts[0].body
    message.parts[0].body = body + unicode_value

    message = scan(message.to_string())
    eq_(body + unicode_value, message.parts[0].body)
    eq_('quoted-printable', message.parts[0].content_encoding.value)


def preserve_ascii_test():
    """Make sure that ascii remains ascii whenever possible"""
    # should remain ascii
    message = scan(TEXT_ONLY)
    message.body = u'Hello, how is it going?'
    message = scan(message.to_string())
    eq_('7bit', message.content_encoding.value)


def ascii_to_unicode_test():
    """Make sure that ascii uprades to unicode whenever needed"""
    # contains unicode chars
    message = scan(TEXT_ONLY)
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'
    message.body = unicode_value
    message = scan(message.to_string())
    eq_('base64', message.content_encoding.value)
    eq_('utf-8', message.content_type.get_charset())
    eq_(unicode_value, message.body)


def correct_charset_test():
    # Given
    message = scan(TEXT_ONLY)
    eq_('iso-8859-1', message.charset)

    # When
    message.charset = 'utf-8'

    # Then
    eq_('utf-8', message.charset)
    eq_('utf-8', str(message.headers['Content-Type'].get_charset()))


def set_message_id_test():
    # Given
    message = scan(MULTI_RECEIVED_HEADERS)

    # When/Then
    eq_({'AANLkTi=1ANR2FzeeQ-vK3-_ty0gUrOsAxMRYkob6CL-c@mail.gmail.com',
         'AANLkTinUdYK2NpEiYCKGnCEp_OXKqst_bWNdBVHsfDVh@mail.gmail.com'},
        set(message.references))


def ascii_to_quoted_printable_test():
    """Make sure that ascii uprades to quoted-printable if it has long lines"""
    # contains unicode chars
    message = scan(TEXT_ONLY)
    value = u'Hello, how is it going?' * 100
    message.body = value
    message = scan(message.to_string())
    eq_('quoted-printable', message.content_encoding.value)
    eq_('iso-8859-1', message.content_type.get_charset())
    eq_('iso-8859-1', message.charset)
    eq_(value, message.body)


def create_message_without_headers_test():
    """Make sure we can't create a message without headers"""
    message = scan(TEXT_ONLY)
    for h,v in message.headers.items():
        del message.headers[h]

    assert_false(message.headers, message.headers)
    assert_raises(EncodingError, message.to_string)


def create_message_without_body_test():
    """Make sure we can't create a message without headers"""
    message = scan(TEXT_ONLY)
    message.body = ""
    message = scan(message.to_string())
    eq_('', message.body)


def torture_alter_test():
    """Alter the complex message, make sure that the structure
    remained the same"""
    message = scan(TORTURE)
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'
    message.parts[5].enclosed.parts[0].parts[0].body = unicode_value
    for p in message.walk():
        if str(p.content_type) == 'text/plain':
            p.body = unicode_value
            p.headers['Mailgun-Altered'] = u'Oh yeah'

    message = scan(message.to_string())

    eq_(unicode_value, message.parts[5].enclosed.parts[0].parts[0].body)

    tree = tree_to_string(message).splitlines()
    expected = TORTURE_PARTS.splitlines()
    eq_(len(tree), len(expected))
    for a, b in zip(expected, tree):
        eq_(a, b)


def walk_test():
    message = scan(ENCLOSED)
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


def to_string_test():
    ok_(str(scan(ENCLOSED)))
    ok_(str(scan(TORTURE)))


def broken_body_test():
    message = scan(ENCLOSED_BROKEN_BODY)
    assert_raises(DecodingError, message.parts[1].enclosed.parts[0]._container._load_body)


def broken_ctype_test():
    """Yahoo fails with russian attachments"""
    message = scan(RUSSIAN_ATTACH_YAHOO)
    assert_raises(
        DecodingError, lambda x: [p.headers for p in message.walk()], 1)

def read_attach_test():
    message = scan(MAILGUN_PIC)
    p = (p for p in message.walk() if p.content_type.main == 'image').next()
    eq_(p.body, MAILGUN_PNG)


def from_python_message_test():
    python_message = message_from_string(MULTIPART)
    message = scan(python_message.as_string())

    eq_(python_message['Subject'], message.headers['Subject'])

    ctypes = [p.get_content_type() for p in python_message.walk()]
    ctypes2 = [p.headers['Content-Type'][0] \
                  for p in message.walk(with_self=True)]
    eq_(ctypes, ctypes2)

    payloads = [p.get_payload(decode=True) for p in python_message.walk()][1:]
    payloads2 = [p.body for p in message.walk()]

    eq_(payloads, payloads2)


def iphone_test():
    message = scan(IPHONE)
    eq_(u'\n\n\n~Danielle', list(message.walk())[2].body)


def content_types_test():
    part = scan(IPHONE)
    eq_((None, {}), part.content_disposition)
    assert_false(part.is_attachment())

    eq_(('inline', {'filename': 'photo.JPG'}), part.parts[1].content_disposition)
    assert_false(part.parts[1].is_attachment())
    ok_(part.parts[1].is_inline())

    part = scan(SPAM_BROKEN_CTYPE)
    eq_((None, {}), part.content_disposition)

    part = scan(MAILGUN_PIC)
    attachment = part.parts[1]
    eq_('image/png', attachment.detected_content_type)
    eq_('png', attachment.detected_subtype)
    eq_('image', attachment.detected_format)
    ok_(not attachment.is_body())

    part = scan(BZ2_ATTACHMENT)
    attachment = part.parts[1]
    eq_('application/x-bzip2', attachment.detected_content_type)
    eq_('x-bzip2', attachment.detected_subtype)
    eq_('application', attachment.detected_format)
    ok_(not attachment.is_body())


def test_is_body():
    part = scan(IPHONE)
    ok_(part.parts[0].is_body())


def message_attached_test():
    message = scan(BOUNCE)
    message = message.get_attached_message()
    eq_('"Foo B. Baz" <foo@example.com>', message.headers['From'])


def message_attached_does_not_exist_test():
    message = scan(IPHONE)
    eq_(None, message.get_attached_message())


def message_remove_headers_test():
    message = scan(TORTURE)
    message.remove_headers('X-Status', 'X-Keywords', 'X-UID', 'Nothere')
    message = scan(message.to_string())
    for h in ('X-Status', 'X-Keywords', 'X-UID', 'Nothere'):
        ok_(h not in message.headers)


def message_alter_body_and_serialize_test():
    message = scan(IPHONE)
    part = list(message.walk())[2]
    part.body = u'Привет, Danielle!\n\n'

    with closing(StringIO()) as out:
        message.to_stream(out)
        message1 = scan(out.getvalue())
        message2 = scan(message.to_string())

    parts = list(message1.walk())
    eq_(3, len(parts))
    eq_(u'Привет, Danielle!\n\n', parts[2].body)

    parts = list(message2.walk())
    eq_(3, len(parts))
    eq_(u'Привет, Danielle!\n\n', parts[2].body)


def alter_message_test_size():
    # check to make sure size is recalculated after header changed
    stream_part = scan(IPHONE)
    size_before = stream_part.size

    stream_part.headers.add('foo', 'bar')
    size_after = stream_part.size

    eq_(size_before, len(IPHONE))
    eq_(size_after, len(stream_part.to_string()))


def message_size_test():
    # message part as a stream
    stream_part = scan(IPHONE)
    eq_(len(IPHONE), stream_part.size)

    # assemble a message part
    text1 = 'Hey there'
    text2 = 'I am a part number two!!!'
    message = multipart('alternative')
    message.append(
        text('plain', text1),
        text('plain', text2))

    eq_(len(message.to_string()), message.size)


def message_convert_to_python_test():
    message = scan(IPHONE)
    a = message.to_python_message()

    for p in message.walk():
        if p.content_type.main == 'text':
            p.body = p.body
    b = message.to_python_message()

    payloads = [p.body for p in message.walk()]
    payloads1 = list(p.get_payload(decode=True) \
                         for p in a.walk() if not p.is_multipart())
    payloads2 = list(p.get_payload(decode=True) \
                         for p in b.walk() if not p.is_multipart())

    eq_(payloads, payloads2)
    eq_(payloads1, payloads2)


def message_is_bounce_test():
    message = scan(BOUNCE)
    ok_(message.is_bounce())

    message = scan(IPHONE)
    assert_false(message.is_bounce())


def message_is_delivery_notification_test():
    message = scan(NDN)
    ok_(message.is_delivery_notification())
    message = scan(BOUNCE)
    ok_(message.is_delivery_notification())

    message = scan(IPHONE)
    assert_false(message.is_delivery_notification())


def read_body_test():
    """ Make sure we've set up boundaries correctly and
    methods that read raw bodies work fine """
    part = scan(MULTIPART)
    eq_(MULTIPART, part._container.read_message())

    # the body of the multipart message is everything after the message
    body = "--bd1" + MULTIPART.split("--bd1", 1)[1]
    eq_(body, part._container.read_body())

    # body of the text part is the value itself
    eq_('Sasha\r\n', part.parts[0]._container.read_body())

    # body of the inner mime part is the part after the headers
    # and till the outer boundary
    body = "--bd2\r\n" + MULTIPART.split(
        "--bd2\r\n", 1)[1].split("--bd1--", 1)[0]
    eq_(body, part.parts[1]._container.read_body())

    # this is a simple message, make sure we can read the body
    # correctly
    part = scan(NO_CTYPE)
    eq_(NO_CTYPE, part._container.read_message())
    eq_("Hello,\nI'm just testing message parsing\n\nBR,\nBob", part._container.read_body())

    # multipart/related
    part = scan(RELATIVE)
    eq_(RELATIVE, part._container.read_message())
    eq_("""This is html and text message, thanks\r\n\r\n-- \r\nRegards,\r\nBob\r\n""", part.parts[0]._container.read_body())

    # enclosed
    part = scan(ENCLOSED)
    eq_(ENCLOSED, part._container.read_message())
    body = part.parts[1]._container.read_body()
    ok_(body.endswith("--===============4360815924781479146==--"))


def test_encode_transfer_encoding():
    body = "long line " * 100
    encoded_body = encode_transfer_encoding('base64', body)
    # according to  RFC 5322 line "SHOULD be no more than 78 characters"
    assert_less(max([len(l) for l in encoded_body.splitlines()]), 79)
