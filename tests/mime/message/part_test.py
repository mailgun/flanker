# coding:utf-8
from contextlib import closing

from nose.tools import eq_, ok_, assert_false, assert_raises, assert_less
from six.moves import StringIO

from flanker import _email
from flanker.mime import recover
from flanker.mime.create import multipart, text
from flanker.mime.message.errors import EncodingError
from flanker.mime.message.part import _encode_transfer_encoding, _base64_decode
from flanker.mime.message.scanner import scan
from tests import (BILINGUAL, BZ2_ATTACHMENT, ENCLOSED, TORTURE, TORTURE_PART,
                   ENCLOSED_BROKEN_ENCODING, EIGHT_BIT, QUOTED_PRINTABLE,
                   TEXT_ONLY, ENCLOSED_BROKEN_BODY, RUSSIAN_ATTACH_YAHOO,
                   MAILGUN_PIC, MAILGUN_PNG, MULTIPART, IPHONE,
                   SPAM_BROKEN_CTYPE, BOUNCE, NDN, NO_CTYPE, RELATIVE,
                   MULTI_RECEIVED_HEADERS, OUTLOOK_EXPRESS)
from tests.mime.message.scanner_test import TORTURE_PARTS, tree_to_string


# We can read the headers and access the body without changing a single
# char inside the message.
def readonly_immutability_test():
    message = scan(BILINGUAL)
    eq_(u"Simple text. How are you? Как ты поживаешь?",
        message.headers['Subject'])
    assert_false(message.was_changed())
    eq_(BILINGUAL, message.to_string())

    message = scan(ENCLOSED)
    pmessage = _email.message_from_string(ENCLOSED)

    # we can read the headers without changing anything
    eq_(u'"Александр Клижентас☯" <bob@example.com>',
        message.headers['To'])
    eq_('Bob Marley <bob@example.net>, Jimmy Hendrix <jimmy@examplehq.com>',
        message.parts[1].enclosed.headers['To'])
    assert_false(message.was_changed())

    # we can also read the body without changing anything
    pbody = pmessage.get_payload()[1].get_payload()[0].get_payload()[0].get_payload(decode=True)
    pbody = pbody.decode('utf-8')
    eq_(pbody, message.parts[1].enclosed.parts[0].body)
    assert_false(message.was_changed())
    eq_(ENCLOSED, message.to_string())


# We can change the headers without changing the body.
def top_level_headers_immutability_test():
    message = scan(ENCLOSED)
    message.headers['Subject'] = u'☯Привет! Как дела? Что делаешь?☯'
    out = message.to_string()
    a = ENCLOSED.split("--===============6195527458677812340==", 1)[1]
    b = out.split("--===============6195527458677812340==", 1)[1]
    eq_(a, b, "Bodies should not be changed in any way")


# We can read the headers without changing a single
# char inside the message.
def immutability_test():
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


# We've changed one part of the message only, the rest was not changed.
def enclosed_first_part_alternation_test():
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


# We've changed the headers in the inner part of the message only,
# the rest was not changed.
def enclosed_header_alternation_test():
    message = scan(ENCLOSED)

    enclosed = message.parts[1].enclosed
    enclosed.headers['Subject'] = u'☯Привет! Как дела? Что делаешь?☯'
    out = message.to_string()

    a = ENCLOSED.split("--===============4360815924781479146==", 1)[1]
    a = a.split("--===============4360815924781479146==--")[0]

    b = out.split("--===============4360815924781479146==", 1)[1]
    b = b.split("--===============4360815924781479146==--")[0]
    eq_(a, b)


# We've changed the headers in the inner part of the message only,
# the rest was not changed.
def enclosed_header_inner_alternation_test():
    message = scan(ENCLOSED)

    unicode_value = u'☯Привет! Как дела? Что делаешь?☯'
    enclosed = message.parts[1].enclosed
    enclosed.parts[0].headers['Subject'] = unicode_value

    message2 = scan(message.to_string())
    enclosed2 = message2.parts[1].enclosed

    eq_(unicode_value, enclosed2.parts[0].headers['Subject'])
    eq_(enclosed.parts[0].body, enclosed2.parts[0].body)
    eq_(enclosed.parts[1].body, enclosed2.parts[1].body)



# We've changed the body in the inner part of the message only,
# the rest was not changed.
def enclosed_body_alternation_test():
    message = scan(ENCLOSED)

    value = u'☯Привет! Как дела? Что делаешь?, \r\n\r Что новенького?☯'
    enclosed = message.parts[1].enclosed
    enclosed.parts[0].body = value
    out = message.to_string()

    message = scan(out)
    enclosed = message.parts[1].enclosed
    eq_(value, enclosed.parts[0].body)


# We've changed the inner part of the entity that has no headers,
# make sure that it was processed correctly.
def enclosed_inner_part_no_headers_test():
    message = scan(TORTURE_PART)

    enclosed = message.parts[1].enclosed
    no_headers = enclosed.parts[0]
    assert_false(no_headers.headers)
    no_headers.body = no_headers.body + "Mailgun!"

    message = scan(message.to_string())
    enclosed = message.parts[1].enclosed
    no_headers = enclosed.parts[0]
    ok_(no_headers.body.endswith("Mailgun!"))


# Make sure we can serialize the message even in case of Decoding errors,
# in this case fallback happens.
def enclosed_broken_encoding_test():
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


# Make sure that content encoding will be preserved if possible.
def preserve_content_encoding_test_8bit():
    # 8bit messages
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'

    # should remain 8bit
    message = scan(EIGHT_BIT)
    message.parts[0].body = unicode_value

    message = scan(message.to_string())
    eq_(unicode_value, message.parts[0].body)
    eq_('8bit', message.parts[0].content_encoding.value)


# Make sure that quoted-printable remains quoted-printable.
def preserve_content_encoding_test_quoted_printable():
    # should remain 8bit
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\r\n Что новенького?☯'
    message = scan(QUOTED_PRINTABLE)
    body = message.parts[0].body
    message.parts[0].body = body + unicode_value

    message = scan(message.to_string())
    eq_(body + unicode_value, message.parts[0].body)
    eq_('quoted-printable', message.parts[0].content_encoding.value)


# Make sure that ascii remains ascii whenever possible.
def preserve_ascii_test():
    # should remain ascii
    message = scan(TEXT_ONLY)
    message.body = u'Hello, how is it going?'
    message = scan(message.to_string())
    eq_('7bit', message.content_encoding.value)


# Make sure that we don't re-serialize a message and change its formatting
# when headers were added but nothing else was modified.
def preserve_formatting_with_new_headers_test():
    # MULTIPART contains this header:
    #   Content-Type: multipart/alternative; boundary=bd1
    # which will change to this if it is re-serialized:
    #   Content-Type: multipart/alternative; boundary="bd1"
    message = scan(MULTIPART)
    message.headers.prepend('X-New-Header', 'Added')
    new_header, remaining_mime = message.to_string().split('\r\n', 1)
    eq_('X-New-Header: Added', new_header)
    eq_(MULTIPART, remaining_mime)


# We don't have to fully parse message headers if they are never accessed.
# Thus we should be able to parse then serialize a message with malformed
# headers without crashing, even though we would crash if we fully parsed it.
def parse_then_serialize_malformed_message_test():
    serialized = scan(OUTLOOK_EXPRESS).to_string()
    eq_(OUTLOOK_EXPRESS, serialized)


# Make sure that ascii uprades to quoted-printable whenever needed.
def ascii_to_quoted_printable_test():
    # contains unicode chars
    message = scan(TEXT_ONLY)
    unicode_value = u'☯Привет! Как дела? Что делаешь?,\n Что новенького?☯'
    message.body = unicode_value
    message = scan(message.to_string())
    eq_('quoted-printable', message.content_encoding.value)
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


# Make sure that ascii uprades to quoted-printable if it has long lines.
def ascii_to_quoted_printable_test_2():
    # contains unicode chars
    message = scan(TEXT_ONLY)
    value = u'Hello, how is it going?' * 100
    message.body = value
    message = scan(message.to_string())
    eq_('quoted-printable', message.content_encoding.value)
    eq_('iso-8859-1', message.content_type.get_charset())
    eq_('iso-8859-1', message.charset)
    eq_(value, message.body)


# Make sure we can't create a message without headers.
def create_message_without_headers_test():
    message = scan(TEXT_ONLY)
    for h,v in message.headers.items():
        del message.headers[h]

    assert_false(message.headers, message.headers)
    assert_raises(EncodingError, message.to_string)


# Make sure we can't create a message without headers.
def create_message_without_body_test():
    message = scan(TEXT_ONLY)
    message.body = ""
    message = scan(message.to_string())
    eq_('', message.body)


# Alter the complex message, make sure that the structure remained the same.
def torture_alter_test():
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


def broken_ctype_test():
    message = scan(RUSSIAN_ATTACH_YAHOO)
    attachment = message.parts[1]
    eq_('image/png', attachment.detected_content_type)
    eq_('png', attachment.detected_subtype)
    eq_('image', attachment.detected_format)
    eq_(u'Картинка с очень, очень длинным предлинным именем преименем таким чт�', attachment.detected_file_name)
    ok_(not attachment.is_body())


def read_attach_test():
    message = scan(MAILGUN_PIC)
    image_parts = [p for p in message.walk() if p.content_type.main == 'image']
    eq_(image_parts[0].body, MAILGUN_PNG)


def from_python_message_test():
    python_message = _email.message_from_string(MULTIPART)
    message = scan(python_message.as_string())

    eq_(python_message['Subject'], message.headers['Subject'])

    ctypes = [p.get_content_type() for p in python_message.walk()]
    ctypes2 = [p.headers['Content-Type'][0]
               for p in message.walk(with_self=True)]
    eq_(ctypes, ctypes2)

    payloads = []
    for p in python_message.walk():
        payload = p.get_payload(decode=True)
        if payload:
            payload = payload.decode('utf-8')
        payloads.append(payload)

    payloads2 = [p.body for p in message.walk()]

    eq_(payloads[1:], payloads2)


def iphone_test():
    message = scan(IPHONE)
    eq_(u'\r\n\r\n\r\n~Danielle', list(message.walk())[2].body)


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
    eq_('mailgun.png', attachment.detected_file_name)
    ok_(not attachment.is_body())

    part = scan(BZ2_ATTACHMENT)
    attachment = part.parts[1]
    eq_('application/x-bzip2', attachment.detected_content_type)
    eq_('x-bzip2', attachment.detected_subtype)
    eq_('application', attachment.detected_format)
    ok_(not attachment.is_body())


# Content-Type and file name are properly detected.
def test_attachments():
    # pdf attachment, file name in Content-Disposition
    data = """Content-Type: application/octet-stream; name="J_S III_W-2.pdf"
Content-Disposition: attachment; filename*="J_S III_W-2.pdf"
Content-Transfer-Encoding: base64

YmxhaGJsYWhibGFo
"""
    part = scan(data)
    eq_('application/pdf', part.detected_content_type)
    eq_('J_S III_W-2.pdf', part.detected_file_name)

    # no attachment
    data = """Content-Type: text; charset=ISO-8859-1

some plain text here
"""
    part = scan(data)
    eq_('text/plain', part.detected_content_type)
    eq_('', part.detected_file_name)

    # inline attachment, file name in Content-Disposition
    data = """Content-Type: image/png
Content-Transfer-Encoding: base64
Content-Disposition: inline; filename=2.png
Content-ID: <FN2JbofqmRT7zIMt8uzW>

YmxhaGJsYWhibGFo
"""
    part = scan(data)
    eq_('image/png', part.detected_content_type)
    eq_('2.png', part.detected_file_name)

    # broken mime
    data = """Content-Type: Нельзя это распарсить адекватно"
Content-Disposition: Да и это тоже
Content-Transfer-Encoding: base64

YmxhaGJsYWhibGFo
"""
    part = recover(data)
    eq_('text/plain', part.detected_content_type)
    eq_('', part.detected_file_name)


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
    payloads1 = [p.get_payload(decode=True)
                 for p in a.walk() if not p.is_multipart()]
    payloads2 = [p.get_payload(decode=True)
                 for p in b.walk() if not p.is_multipart()]

    eq_(3, len(payloads))
    eq_(payloads[0], payloads2[0].decode('utf-8'))
    eq_(payloads[1], payloads2[1])
    eq_(payloads[2], payloads2[2].decode('utf-8'))
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


# Make sure we've set up boundaries correctly and
# methods that read raw bodies work fine.
def read_body_test():
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
    eq_("Hello,\r\nI'm just testing message parsing\r\n\r\nBR,\r\nBob",
        part._container.read_body())

    # multipart/related
    part = scan(RELATIVE)
    eq_(RELATIVE, part._container.read_message())
    eq_("This is html and text message, thanks\r\n\r\n-- \r\nRegards,\r\nBob\r\n",
        part.parts[0]._container.read_body())

    # enclosed
    part = scan(ENCLOSED)
    eq_(ENCLOSED, part._container.read_message())
    body = part.parts[1]._container.read_body()
    ok_(body.endswith("--===============4360815924781479146==--"))


def test_encode_transfer_encoding():
    body = "long line " * 100
    encoded_body = _encode_transfer_encoding('base64', body)
    # according to  RFC 5322 line "SHOULD be no more than 78 characters"
    assert_less(max([len(l) for l in encoded_body.splitlines()]), 79)


# Test base64 decoder.
def test_base64_decode():
    eq_(b"hello", _base64_decode("aGVs\r\nbG8="))  # valid base64
    eq_(b"hello!", _base64_decode("a\x00GVsbG8\t*hx"))  # trim last character
    eq_(b"hello", _base64_decode("aGVsb\r\nG8"))  # recover single byte padding
    eq_(b"hello!!", _base64_decode("aGVs\rbG8h\nIQ")) # recover 2 bytes padding
    eq_(b"hello!!", _base64_decode("aGЫVs\rЫЫbG8hЫЫ\nЫЫIQ"))
    eq_(b"hello!!", _base64_decode("ЫaGVsbG8h\nIQЫ"))
    eq_(b"hello!!", _base64_decode("ЫЫЫЫaGVsЫЫЫЫ\rbG8h\nIQЫЫЫЫ"))


# Make sure broken base64 part gets recovered.
def broken_body_test():
    message = scan(ENCLOSED_BROKEN_BODY)
    ok_(message.parts[1].enclosed.parts[0].body.startswith("dudes..."))
