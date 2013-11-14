import logging
import email
from flanker.mime.message.scanner import ContentType
from flanker.mime.message import utils, charsets, headers
from flanker.mime.message.headers import parametrized

log = logging.getLogger(__name__)

class FallbackMimePart(object):

    def __init__(self, python_message):
        self.m = python_message
        self._is_root = False

    def is_body(self):
        return (self.content_type.format_type == 'text' or
                 self.content_type.format_type == 'message')

    def is_root(self):
        return self._is_root

    def set_root(self, value):
        self._is_root = value

    def append(self, message):
        self.m.attach(
            FallbackMimePart(
                email.message_from_string(
                    message.to_string())))

    def remove_headers(self, *headers):
        for header in headers:
            if header in self.headers:
                del self.headers[header]

    def is_bounce(self):
        return False

    @property
    def bounce(self):
        return None

    def to_python_message(self):
        return self.m

    def get_attached_message(self):
        """
        Returns attached message if found, None otherwize
        """
        try:
            for part in self.walk(with_self=True):
                if part.content_type == 'message/rfc822':
                    for p in part.walk():
                        return p
        except Exception:
            log.exception("Failed to get attached message")
            return None

    def walk(self, with_self=False, skip_enclosed=False):
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

    @property
    def content_type(self):
        return ContentType(
            self.m.get_content_maintype(),
            self.m.get_content_subtype(),
            dict(self.m.get_params() or []))

    @property
    def charset(self):
        return self.content_type.params.get('charset', 'ascii')

    @property
    def headers(self):
        return FallbackHeaders(self.m)

    @property
    def body(self):
        if not self.m.is_multipart():
            return charsets.convert_to_unicode(
                self.charset,
                self.m.get_payload(decode=True))

    @body.setter
    def body(self, value):
        if not self.m.is_multipart():
            return self.m.set_payload(
                value.encode('utf-8'), 'utf-8')

    @property
    def parts(self):
        if self.m.is_multipart():
            return [FallbackMimePart(p) for p in self.m.get_payload() if p]
        else:
            return []

    @property
    def enclosed(self):
        if self.content_type == 'message/rfc822':
            return FallbackMimePart(self.m.get_payload()[0])

    @property
    def size(self):
        if not self.m.is_multipart():
            return len(self.m.get_payload(decode=False))
        else:
            return sum(p.size for p in self.parts)

    @property
    def content_encoding(self):
        return self.m.get('Content-Transfer-Encoding')

    @content_encoding.setter
    def content_encoding(self, value):
        pass

    @property
    def content_disposition(self):
        try:
            return parametrized.decode(
                self.m.get('Content-Disposition', ''))
        except:
            return (None, {})

    def to_string(self):
        return utils.python_message_to_string(self.m)

    def to_stream(self, out):
        out.write(self.to_string())

    def is_attachment(self):
        return self.content_disposition[0] == 'attachment'

    def is_inline(self):
        return self.content_disposition[0] == 'inline'

    def is_delivery_notification(self):
        ctype = self.content_type
        return  ctype == 'multipart/report'\
            and ctype.params.get('report-type') == 'delivery-status'

    def __str__(self):
        return "FallbackMimePart"

def try_decode(key, value):
    if isinstance(value, (tuple, list)):
        return value
    elif isinstance(value, str):
        try:
            return headers.parse_header_value(key, value)
        except Exception:
            return unicode(value, 'utf-8', 'ignore')
    elif isinstance(value, unicode):
        return value
    else:
        return ""

class FallbackHeaders(object):

    def __init__(self, message):
        self.m = message

    def __getitem__(self, key):
        return try_decode(key, self.m.get(key))

    def __len__(self):
        return len(self.m._headers)

    def __contains__(self, key):
        return key in self.m

    def __setitem__(self, key, value):
        if key in self.m:
            del self.m[key]
        self.m[key] = headers.to_mime(key, value)

    def __delitem__(self, key):
        del self.m[key]

    def __nonzero__(self):
        return len(self.m) > 0

    def __iter__(self):
        for key, val in self.iteritems():
            yield (key, val)

    def prepend(self, key, val):
        self.m._headers.insert(0, (key, val))

    def add(self, key, value):
        self.m[key] = headers.to_mime(key, value)

    def keys(self):
        return self.m.keys()

    def items(self):
        return [(key,val) for (key, val) in self.iteritems()]

    def iteritems(self):
        for key, val in self.m.items():
            yield (key, try_decode(key, val))

    def get(self, key, default=None):
        val = try_decode(key, self.m.get(key, default))
        return val if val is not None else default

    def getall(self, key):
        return [try_decode(key, v) for v in self.m.get_all(key, [])]

    def __str__(self):
        return str(self.m._headers)
