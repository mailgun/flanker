import logging
import email
from webob.multidict import MultiDict
from flanker.mime.message.charsets import convert_to_unicode
from flanker.mime.message.headers.headers import remove_newlines, MimeHeaders
from flanker.mime.message.part import RichPartMixin
from flanker.mime.message.scanner import ContentType
from flanker.mime.message import utils, headers
from flanker.mime.message.headers import parametrized, normalize

log = logging.getLogger(__name__)


class FallbackMimePart(RichPartMixin):

    def __init__(self, message):
        RichPartMixin.__init__(self, is_root=False)
        self._m = message
        self._headers = FallbackHeaders(message)
        self._body = None

    @property
    def size(self):
        if not self._m.is_multipart():
            return len(self._m.get_payload(decode=False))
        else:
            return sum(p.size for p in self.parts)

    @property
    def headers(self):
        return self._headers

    @property
    def content_type(self):
        return ContentType(self._m.get_content_maintype(),
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
        if self._body:
            return self._body

        if self.content_type.is_delivery_status():
            self._body = self._m.get_payload(decode=True)
            if self._body is None:
                self._body = "\r\n".join(str(p) for p in self._m.get_payload())

        elif not self._m.is_multipart():
            self._body = self._m.get_payload(decode=True)
            if self._m.get_content_maintype() == 'text':
                self._body = convert_to_unicode(self.charset, self._body)

        return self._body

    @body.setter
    def body(self, value):
        self._body = None
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


class FallbackHeaders(MimeHeaders):

    def __init__(self, message):
        MimeHeaders.__init__(self, [(k, _try_decode(k, v))
                                    for k, v in message.items()])
        self._m = message

    def __setitem__(self, key, value):
        MimeHeaders.__setitem__(self, key, value)
        del self._m[key]
        self._m[key] = remove_newlines(value)

    def __delitem__(self, key):
        MimeHeaders.__delitem__(self, key)
        del self._m[key]

    def prepend(self, key, value):
        MimeHeaders.prepend(self, key, value)
        self._m._headers.insert(0, (normalize(key), remove_newlines(value)))

    def add(self, key, value):
        MimeHeaders.add(self, key, value)
        self._m[key] = headers.to_mime(normalize(key), remove_newlines(value))

    def transform(self, func):
        changed = [False]

        def wrapped_func(key, value):
            new_key, new_value = func(key, value)
            if new_value != value or new_key != key:
                changed[0] = True
            return new_key, new_value

        transformed_headers = [wrapped_func(k, v) for k, v in self._m.items()]
        if changed[0]:
            self._m._headers = transformed_headers
            self._v = MultiDict([(normalize(k), remove_newlines(v))
                                 for k, v in transformed_headers])
            self.changed = True


def _try_decode(key, value):
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


