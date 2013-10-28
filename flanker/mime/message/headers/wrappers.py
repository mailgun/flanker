""" Useful wrappers for headers with parameters,
provide some convenience access methods
"""

import regex as re
import flanker.addresslib.address

from email.utils import make_msgid


class WithParams(tuple):

    def __new__(self, value, params=None):
        return tuple.__new__(self, (value, params or {}))

    @property
    def value(self):
        return tuple.__getitem__(self, 0)

    @property
    def params(self):
        return tuple.__getitem__(self, 1)


class ContentType(tuple):

    def __new__(self, main, sub, params=None):
        return tuple.__new__(
            self, (main.lower() + '/' + sub.lower(), params or {}))

    def __init__(self, main, sub, params={}):
        self.main = main
        self.sub = sub

    @property
    def value(self):
        return tuple.__getitem__(self, 0)

    @property
    def params(self):
        return tuple.__getitem__(self, 1)

    @property
    def format_type(self):
        return tuple.__getitem__(self, 0).split('/')[0]

    @property
    def subtype(self):
        return tuple.__getitem__(self, 0).split('/')[1]


    def is_content_type(self):
        return True

    def is_boundary(self):
        return False

    def is_end(self):
        return False

    def is_singlepart(self):
        return self.main != 'multipart' and\
            self.main != 'message' and\
            not self.is_headers_container()

    def is_multipart(self):
        return self.main == 'multipart'

    def is_headers_container(self):
        return self.is_feedback_report() or \
            self.is_rfc_headers() or \
            self.is_disposition_notification()

    def is_rfc_headers(self):
        return self == 'text/rfc822-headers'

    def is_message_container(self):
        return self == 'message/rfc822'

    def is_disposition_notification(self):
        return self == 'message/disposition-notification'

    def is_delivery_status(self):
        return self == 'message/delivery-status'

    def is_feedback_report(self):
        return self == 'message/feedback-report'

    def is_delivery_report(self):
         return self == 'multipart/report'

    def get_boundary(self):
        return self.params.get("boundary")

    def get_boundary_line(self, final=False):
        return "--{}{}".format(
            self.get_boundary(), "--" if final else "")

    def get_charset(self):
        return self.params.get("charset", 'ascii').lower()

    def set_charset(self, value):
        self.params["charset"] = value.lower()

    def __str__(self):
        return "{}/{}".format(self.main, self.sub)

    def __eq__(self, other):
        if isinstance(other, ContentType):
            return self.main == other.main \
                and self.sub == other.sub \
                and self.params == other.params
        elif isinstance(other, tuple):
            return tuple.__eq__(self, other)
        elif isinstance(other, (unicode, str)):
            return str(self) == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class MessageId(str):

    RE_ID = re.compile("<([^<>]+)>", re.I)
    MIN_LENGTH = 5
    MAX_LENGTH = 256

    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def __clean(self):
        return self.replace('"','').replace("'", '')

    def __hash__(self):
        return hash(self.__clean())

    def __eq__(self, other):
        if isinstance(other, MessageId):
            return self.__clean() == other.__clean()
        else:
            return self.__clean() == str(other)

    @classmethod
    def from_string(cls, string):
        if not isinstance(string, (str, unicode)):
            return None
        for message_id in cls.scan(string):
            return message_id

    @classmethod
    def generate(cls, domain=None):
        message_id = make_msgid().strip("<>")
        if domain:
            local = message_id.split('@')[0]
            message_id = "{}@{}".format(local, domain)
        return cls(message_id)

    @classmethod
    def is_valid(cls, s):
        return cls.MIN_LENGTH < len(s) < cls.MAX_LENGTH and \
            flanker.addresslib.address.is_email(s)

    @classmethod
    def scan(cls, string):
        for m in cls.RE_ID.finditer(string):
            message_id = m.group(1)
            if cls.is_valid(message_id):
                yield cls(message_id)


class Subject(str):
    RE_RE = re.compile("((RE|FW|FWD|HA)([[]\d])*:\s*)*", re.I)

    def __new__(cls, *args, **kw):
        return str.__new__(cls, *args, **kw)

    def strip_replies(self):
        return self.RE_RE.sub('', self)

