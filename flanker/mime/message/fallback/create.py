import email
from flanker.mime.message.fallback.part import FallbackMimePart

def from_string(string):
    return FallbackMimePart(email.message_from_string(string))

def from_python(message):
    return FallbackMimePart(message)
