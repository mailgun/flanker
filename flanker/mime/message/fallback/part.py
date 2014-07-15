import logging
import email
from flanker.mime.message.part import ReachPartMixin
from flanker.mime.message.scanner import ContentType
from flanker.mime.message import utils, charsets, headers
from flanker.mime.message.headers import parametrized

log = logging.getLogger(__name__)


class FallbackMimePart(ReachPartMixin):

    def __init__(self, python_message):
        ReachPartMixin.__init__(self, is_root=False)
        self._m = python_message

    @property
    def size(self):
        if not self._m.is_multipart():
            return len(self._m.get_payload(decode=False))
        else:
            return sum(p.size for p in self.parts)

    @property
    def headers(self):
        return FallbackHeaders(self._m)

    @property
    def content_type(self):
        return ContentType(
            self._m.get_content_maintype(),
            self._m.get_content_subtype(),
            dict(self._m.get_params() or []))

    @property
    def content_disposition(self):
        try:
            return parametrized.decode(self._m.get('Content-Disposition', ''))
        except:
            return None, {}

    @property
    def content_encoding(self):
        return self._m.get('Content-Transfer-Encoding')

    @content_encoding.setter
    def content_encoding(self, value):
        pass  # FIXME Not implement

    @property
    def body(self):
        if self.content_type.is_delivery_status():
            body = self._m.get_payload(decode=True)
            if body:
                return body
            return "\r\n".join(str(p) for p in self._m.get_payload())
        if not self._m.is_multipart():
            return charsets.convert_to_unicode(
                self.charset, self._m.get_payload(decode=True))

    @body.setter
    def body(self, value):
        if not self._m.is_multipart():
            self._m.set_payload(value.encode('utf-8'), 'utf-8')

    @property
    def charset(self):
        return self.content_type.get_charset()

    @charset.setter
    def charset(self, value):
        pass  # FIXME Not implement

    def to_string(self):
        return utils.python_message_to_string(self._m)

    def to_stream(self, out):
        out.write(self.to_string())

    def was_changed(self):
        return False  # FIXME Not implement

    def to_python_message(self):
        return self._m

    def append(self, *messages):
        for m in messages:
            part = FallbackMimePart(email.message_from_string(m.to_string()))
            self._m.attach(part)

    @property
    def parts(self):
        if self._m.is_multipart():
            return [FallbackMimePart(p) for p in self._m.get_payload() if p]
        else:
            return []

    @property
    def enclosed(self):
        if self.content_type == 'message/rfc822':
            return FallbackMimePart(self._m.get_payload()[0])

    def enclose(self, message):
        pass  # FIXME Not implemented



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
        return [(key, val) for (key, val) in self.iteritems()]

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
