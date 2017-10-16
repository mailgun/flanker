from collections import deque
from contextlib import closing

import attr
import regex as re
import six
from attr.validators import instance_of
from six.moves import range

from flanker.mime.message.headers import MimeHeaders
from flanker.mime.message.headers.parsing import parse_stream


_HEADERS = ('Action',
            'Content-Description',
            'Diagnostic-Code',
            'Final-Recipient',
            'Received',
            'Remote-Mta',
            'Reporting-Mta',
            'Status')

_RE_STATUS = re.compile(r'\d\.\d+\.\d+', re.IGNORECASE)


@attr.s(frozen=True)
class Result(object):
    score = attr.ib(validator=instance_of(float))
    status = attr.ib(validator=instance_of(six.text_type))
    diagnostic_code = attr.ib(validator=instance_of(six.text_type))
    notification = attr.ib(validator=instance_of(six.text_type))

    def is_bounce(self, probability=0.3):
        return self.score > probability


def detect(message):
    headers = _collect_headers(message)
    return Result(score=len(headers) / float(len(_HEADERS)),
                  status=_get_status(headers),
                  diagnostic_code=headers.get('Diagnostic-Code', u''),
                  notification=_get_notification(message))


def _collect_headers(message):
    collected = deque()
    for p in message.walk(with_self=True):
        for h in _HEADERS:
            if h in p.headers:
                collected.append((h, p.headers[h]))
        if p.content_type.is_delivery_status():
            collected += _collect_headers_from_status(p.body)

    return MimeHeaders(collected)


def _collect_headers_from_status(body):
    out = deque()
    with closing(six.StringIO(body)) as stream:
        for i in range(3):
            out += parse_stream(stream)

    return out


def _get_status(headers):
    for v in headers.getall('Status'):
        if _RE_STATUS.match(v.strip()):
            return v

    return u''


def _get_notification(message):
    for part in message.walk():
        content_desc = part.headers.get('Content-Description', '').lower()
        if content_desc == 'notification':
            return part.body

    return u''
