import email.utils
import email.encoders
import logging
import mimetypes
import imghdr

from contextlib import closing
from cStringIO import StringIO
from os import path

from email.mime import audio

from flanker.utils import is_pure_ascii
from flanker.mime import bounce
from flanker.mime.message import headers, charsets
from flanker.mime.message.headers import WithParams, ContentType, MessageId, Subject
from flanker.mime.message.headers.parametrized import fix_content_type
from flanker.mime.message.errors import EncodingError, DecodingError

log = logging.getLogger(__name__)

CTE = WithParams('7bit', {})

class Stream(object):

    def __init__(self, content_type, start, end, string, stream):
        self.content_type = content_type
        self.start = start
        self.end = end
        self.string = string
        self.stream = stream

        self._headers = None
        self._body_start = None
        self._body = None
        self._body_changed = False
        self.size = len(self.string)

    @property
    def headers(self):
        self._load_headers()
        return self._headers

    @property
    def body(self):
        self._load_body()
        return self._body

    @body.setter
    def body(self, value):
        self._set_body(value)

    def read_message(self):
        self.stream.seek(self.start)
        return self.stream.read(self.end - self.start + 1)

    def read_body(self):
        self._load_headers()
        self.stream.seek(self._body_start)
        return self.stream.read(self.end - self._body_start + 1)

    def _load_headers(self):
        if self._headers is None:
            self.stream.seek(self.start)
            self._headers = headers.MimeHeaders.from_stream(self.stream)
            self._body_start = self.stream.tell()

    def _load_body(self):
        if self._body is None:
            self._load_headers()
            self.stream.seek(self._body_start)
            self._body = decode_body(
                self.content_type,
                self.headers.get('Content-Transfer-Encoding', CTE).value,
                self.stream.read(self.end - self._body_start + 1))

    def _set_body(self, value):
        self._body = value
        self._body_changed = True


    def headers_changed(self):
        return self._headers is not None and self._headers.have_changed()

    def body_changed(self):
        return self._body_changed


def adjust_content_type(content_type, body=None, filename=None):
    """Adjust content type based on filename or body contents
    """
    if filename and str(content_type) == 'application/octet-stream':
        guessed = mimetypes.guess_type(filename)[0]
        if guessed:
            main, sub = fix_content_type(
                guessed, default=('application', 'octet-stream'))
            content_type = ContentType(main, sub)

    if content_type.main == 'image' and body:
        sub = imghdr.what(None, body)
        if sub:
            content_type = ContentType('image', sub)

    elif content_type.main == 'audio' and body:
        sub = audio._whatsnd(body)
        if sub:
            content_type = ContentType('audio', sub)

    return content_type


class Body(object):
    def __init__(
        self, content_type, body, charset=None, disposition=None, filename=None):
        self.headers = headers.MimeHeaders()
        self.body = body
        self.disposition = disposition or ('attachment' if filename else None)
        self.filename = filename
        self.size = len(body)

        if self.filename:
            self.filename = path.basename(self.filename)

        content_type = adjust_content_type(content_type, body, filename)

        if content_type.main == 'text':
            # the text should have a charset
            if not charset:
                charset = "utf-8"

            # it should be stored as unicode. period
            self.body = charsets.convert_to_unicode(charset, body)

            # let's be simple when possible
            if charset != 'ascii' and is_pure_ascii(body):
                charset = 'ascii'

        self.headers['MIME-Version'] = '1.0'
        self.headers['Content-Type'] = content_type
        if charset:
            content_type.params['charset'] = charset

        if self.disposition:
            self.headers['Content-Disposition'] = WithParams(disposition)
            if self.filename:
                self.headers['Content-Disposition'].params['filename'] = self.filename
                self.headers['Content-Type'].params['name'] = self.filename

    @property
    def content_type(self):
        return self.headers['Content-Type']

    def headers_changed(self):
        return True

    def body_changed(self):
        return True


class Part(object):

    def __init__(self, ctype):
        self.headers = headers.MimeHeaders()
        self.body = None
        self.headers['Content-Type'] = ctype
        self.headers['MIME-Version'] = '1.0'
        self.size = 0

    @property
    def content_type(self):
        return self.headers['Content-Type']

    def headers_changed(self):
        return True

    def body_changed(self):
        return True


class MimePart(object):
    def __init__(self, container, parts=None, enclosed=None, is_root=False):

        self._container = container
        self._is_root = is_root
        self._bounce = None

        self.parts = parts or []
        self.enclosed = enclosed

    @property
    def size(self):
        """ Returns message size in bytes"""
        if isinstance(self._container, Stream):
            return self._container.size
        else:
            return sum(part._container.size
                       for part in self.walk(with_self=True))

    @property
    def headers(self):
        """Returns multi dictionary with headers converted to unicode,
        headers like Content-Type, Content-Disposition are tuples
        ("value", {"param": "val"})"""
        return self._container.headers

    @property
    def content_type(self):
        """ returns object with properties:
        main - main part of content type
        sub - subpart of content type
        params - dictionary with parameters
        """
        return self._container.content_type

    @property
    def content_disposition(self):
        """ returns tuple (value, params) """
        return self.headers.get('Content-Disposition', WithParams(None))

    @property
    def content_encoding(self):
        return self.headers.get(
            'Content-Transfer-Encoding', WithParams('7bit'))

    @content_encoding.setter
    def content_encoding(self, value):
        self.headers['Content-Transfer-Encoding'] = value

    @property
    def body(self):
        """ returns decoded body """
        if self.content_type.is_singlepart()\
                or self.content_type.is_delivery_status():
            return self._container.body

    @body.setter
    def body(self, value):
        if self.content_type.is_singlepart()\
                or self.content_type.is_delivery_status():
            self._container.body = value

    @property
    def charset(self):
        return self.content_type.get_charset()

    @charset.setter
    def charset(self, value):
        charset = value.lower()
        self.content_type.set_charset(value)
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = ContentType('text', 'plain', {})
        self.headers['Content-Type'].params['charset'] = charset
        self.headers.changed = True

    @property
    def message_id(self):
        return MessageId.from_string(self.headers.get('Message-Id', ''))

    @message_id.setter
    def message_id(self, value):
        if not MessageId.is_valid(value):
            raise ValueError("invalid message id format")
        self.headers['Message-Id'] = "<{}>".format(value)

    @property
    def subject(self):
        return self.headers.get('Subject', '')

    @property
    def clean_subject(self):
        """
        Subject without re, fw, fwd, HA prefixes
        """
        return Subject(self.subject).strip_replies()

    @property
    def references(self):
        """
        Retunrs message-ids referencing the message
        in accordance to jwz threading algo
        """
        refs = list(MessageId.scan(self.headers.get('References', '')))
        if not refs:
            reply = MessageId.from_string(self.headers.get('In-Reply-To', ''))
            if reply:
                refs.append(reply[0])
        return refs

    @property
    def detected_format(self):
        return self.detected_content_type.format_type

    @property
    def detected_subtype(self):
        return self.detected_content_type.subtype

    @property
    def detected_content_type(self):
        """Returns content type based on the body
        content, file name and original content type
        supplied inside the message
        """
        return adjust_content_type(
            self.content_type, filename=self.detected_file_name)

    @property
    def detected_file_name(self):
        """Detects file name based on content type
        or part name
        """
        ctype = self.content_type
        file_name = ctype.params.get('name', '') or ctype.params.get('filename', '')

        cdisp = self.content_disposition
        if cdisp.value == 'attachment':
            file_name = cdisp.params.get('filename', '') or file_name

        # filenames can be presented as tuples, like:
        # ('us-ascii', 'en-us', 'image.jpg')
        if isinstance(file_name, tuple) and len(file_name) == 3:
            # encoding permissible to be empty
            encoding = file_name[0]
            if encoding:
                file_name = file_name[2].decode(encoding)
            else:
                file_name = file_name[2]

        file_name = headers.mime_to_unicode(file_name)
        return file_name

    def is_root(self):
        return self._is_root

    def set_root(self, val):
        self._is_root = bool(val)

    def to_string(self):
        """ returns MIME representation of the message"""
        # this optimisation matters *A LOT*
        # we submit the original string,
        # no copying, no alternation, yeah!
        if self.is_root() and not self.was_changed():
            return self._container.string
        else:
            with closing(StringIO()) as out:
                self.to_stream(out)
                return out.getvalue()

    def to_stream(self, out):
        """ serialzes the message using file like object """
        if not self.was_changed():
            out.write(self._container.read_message())
        else:
            try:
                original_position = out.tell()
                self.to_stream_when_changed(out)
            except DecodingError:
                out.seek(original_position)
                out.write(self._container.read_message())

    def to_stream_when_changed(self, out):

        ctype = self.content_type

        if ctype.is_singlepart():

            if self._container.body_changed():
                charset, encoding, body = encode_body(self)
                if charset:
                    self.charset = charset
                self.content_encoding = WithParams(encoding)
            else:
                body = self._container.read_body()

            # RFC allows subparts without headers
            if self.headers:
                self.headers.to_stream(out)
            elif self.is_root():
                raise EncodingError("Root message should have headers")

            out.write(CRLF)
            out.write(body)
        else:
            self.headers.to_stream(out)
            out.write(CRLF)

            if ctype.is_multipart():
                boundary = ctype.get_boundary_line()
                for index, part in enumerate(self.parts):
                    out.write(
                        (CRLF if index != 0 else "") + boundary + CRLF)
                    part.to_stream(out)
                out.write(CRLF + ctype.get_boundary_line(final=True) + CRLF)

            elif ctype.is_message_container():
                self.enclosed.to_stream(out)

    def was_changed(self):
        if self._container.headers_changed():
            return True

        if self.content_type.is_singlepart():
            if self._container.body_changed():
                return True

        elif self.content_type.is_multipart():
            return any(p.was_changed() for p in self.parts)

        elif self.content_type.is_message_container():
            return self.enclosed.was_changed()

    def walk(self, with_self=False, skip_enclosed=False):
        """ Returns iterator object traversing through the message parts,
        if you want to include the top level part into the iteration, use
        'with_self' parameter. If you don't want to include parts of
        enclosed messages, use 'skip_enclosed' parameter. Each part itself
        provides headers, content_type and body members.
        """
        if with_self:
            yield self

        if self.content_type.is_multipart():
            for p in self.parts:
                yield p
                for x in p.walk(False, skip_enclosed=skip_enclosed):
                    yield x

        elif self.content_type.is_message_container() and not skip_enclosed:
            yield self.enclosed
            for p in self.enclosed.walk(False):
                yield p

    def is_attachment(self):
        return self.content_disposition.value == 'attachment'

    def is_body(self):
        return (not self.detected_file_name and
                (self.content_type.format_type == 'text' or
                 self.content_type.format_type == 'message'))

    def is_inline(self):
        return self.content_disposition.value == 'inline'

    def is_delivery_notification(self):
        """ Tells whether a message is a system delivery notification """
        ctype = self.content_type
        return  ctype == 'multipart/report'\
            and ctype.params.get('report-type') == 'delivery-status'

    def get_attached_message(self):
        """ Returns attached message if found, None otherwize"""
        try:
            for part in self.walk(with_self=True):
                if part.content_type == 'message/rfc822':
                    for p in part.walk():
                        return p
        except Exception:
            log.exception("Failed to get attached message")
            return None

    def remove_headers(self, *headers):
        """Removes all passed headers name in one operation"""
        for header in headers:
            if header in self.headers:
                del self.headers[header]

    def to_python_message(self):
        return email.message_from_string(self.to_string())

    @property
    def bounce(self):
        """ If the message is bounce, retuns bounce object that
        provides the values:

        score - between 0 and 1
        status -  delivery status
        notification - human readable description
        diagnostic_code - smtp diagnostic codes

        Can raise MimeError in case if MIME is screwed
        """
        if not self._bounce:
            self._bounce = bounce.detect(self)
        return self._bounce

    def is_bounce(self, threshold=0.3):
        """
        Determines whether the message is a bounce message based on
        given threshold.  0.3 is a good conservative base.
        """
        return self.bounce.score > threshold

    def enclose(self, message):
        self.enclosed = message
        message.set_root(False)

    def append(self, *messages):
        for m in messages:
            self.parts.append(m)
            m.set_root(False)

    def __str__(self):
        return "({})".format(self.content_type)


def decode_body(content_type, content_encoding, body):
    # decode the transfer encoding
    try:
        body = decode_transfer_encoding(
                    content_encoding, body)
    except Exception:
        raise DecodingError("Failed to decode body")

    # decode the charset next
    return decode_charset(content_type, body)


def decode_transfer_encoding(encoding, body):
    if encoding == 'base64':
        return email.utils._bdecode(body)
    elif encoding == 'quoted-printable':
        return email.utils._qdecode(body)
    else:
        return body

def decode_charset(ctype, body):
    if ctype.main != 'text':
        return body

    charset = ctype.get_charset()
    body = charsets.convert_to_unicode(charset, body)

    # for text/html unicode bodies make sure to replace
    # the whitespace (0xA0) with &nbsp; Outlook is reported to
    # have a bug there
    if ctype.sub =='html' and charset == 'utf-8':
        # Outlook bug
        body = body.replace(u'\xa0', u'&nbsp;')

    return body


def encode_body(part):
    content_type = part.content_type
    content_encoding = part.content_encoding.value
    body = part._container.body

    charset = content_type.get_charset()
    if content_type.main == 'text':
        charset, body = encode_charset(charset, body)
        content_encoding = choose_text_encoding(
            charset, content_encoding, body)
    else:
        content_encoding = 'base64'

    body = encode_transfer_encoding(content_encoding, body)
    return charset, content_encoding, body


def encode_charset(preferred_charset, text):
    try:
        charset = preferred_charset or 'ascii'
        text = text.encode(preferred_charset)
    except:
        charset = 'utf-8'
        text = text.encode(charset)
    return charset, text


def encode_transfer_encoding(encoding, body):
    if encoding == 'quoted-printable':
        return email.encoders._qencode(body)
    elif encoding == 'base64':
        return email.encoders._bencode(body)
    else:
        return body


def choose_text_encoding(charset, preferred_encoding, body):
    if charset in ('ascii', 'iso-8859-1', 'us-ascii'):
        if has_long_lines(body):
            return stronger_encoding(preferred_encoding, 'quoted-printable')
        else:
            return preferred_encoding
    else:
        return stronger_encoding(preferred_encoding, 'base64')


def stronger_encoding(a, b):
    weights = {'7bit': 0, 'quoted-printable': 1, 'base64': 1, '8bit': 3}
    if weights.get(a, -1) >= weights[b]:
        return a
    return b


def has_long_lines(text, max_line_len=599):
    '''
    Returns True if text contains lines longer than a certain length.
    Some SMTP servers (Exchange) refuse to accept messages "wider" than
    certain length.
    '''
    if not text:
        return False
    for line in text.splitlines():
        if len(line) >= max_line_len:
            return True
    return False

CRLF = "\r\n"
