""" This package is a set of utilities and methods for building mime messages """

import uuid
from flanker.mime.message import ContentType, utils
from flanker.mime.message.part import MimePart, Body, Part, adjust_content_type
from flanker.mime.message import scanner
from flanker.mime.message.headers.parametrized import fix_content_type
from flanker.mime.message.headers import WithParams

def multipart(subtype):
    return MimePart(
        container=Part(
            ContentType(
                "multipart", subtype, {"boundary": uuid.uuid4().hex})),
        is_root=True)


def message_container(message):
    part = MimePart(
        container=Part(ContentType("message", "rfc822")),
        enclosed=message)
    message.set_root(False)
    return part


def text(subtype, body, charset=None, disposition=None, filename=None):
    return MimePart(
        container=Body(
            content_type=ContentType("text", subtype),
            body=body,
            charset=charset,
            disposition=disposition,
            filename=filename),
        is_root=True)


def binary(maintype, subtype, body, filename=None, disposition=None, charset=None):
    return MimePart(
        container=Body(
            content_type=ContentType(maintype, subtype),
            body=body,
            charset=charset,
            disposition=disposition,
            filename=filename),
        is_root=True)


def attachment(content_type, body, filename=None, disposition=None, charset=None):
    """Smarter method to build attachments that detects the proper content type
    and form of the message based on content type string, body and filename
    of the attachment
    """

    # fix and sanitize content type string and get main and sub parts:
    main, sub = fix_content_type(
        content_type, default=('application', 'octet-stream'))

    # adjust content type based on body or filename if it's not too accurate
    content_type = adjust_content_type(
        ContentType(main, sub), body, filename)

    if content_type.main == 'message':
        message = message_container(from_string(body))
        message.headers['Content-Disposition'] = WithParams(disposition)
        return message
    else:
        return binary(
            content_type.main,
            content_type.sub,
            body, filename,
            disposition,
            charset)


def from_string(string):
    return scanner.scan(string)


def from_python(message):
    return from_string(
        utils.python_message_to_string(message))


def from_message(message):
    return from_string(message.to_string())

