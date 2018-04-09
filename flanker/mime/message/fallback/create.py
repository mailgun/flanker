import email

import six

from flanker.mime.message.fallback.part import FallbackMimePart


def from_string(string):
    if six.PY3 and isinstance(string, six.binary_type):
        string = string.decode('utf-8')

    return FallbackMimePart(email.message_from_string(string))


def from_python(message):
    return FallbackMimePart(message)
