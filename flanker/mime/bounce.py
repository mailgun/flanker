import regex as re
from collections import deque
from contextlib import closing
from cStringIO import StringIO
from flanker.mime.message.headers.parsing import parse_stream
from flanker.mime.message.headers import MimeHeaders


def detect(message):
    headers = collect(message)
    return Result(
        score=len(headers) / float(len(HEADERS)),
        status=get_status(headers),
        notification=get_notification(message),
        diagnostic_code=headers.get('Diagnostic-Code'))


def collect(message):
    collected = deque()
    for p in message.walk(with_self=True):
        for h in HEADERS:
            if h in p.headers:
                collected.append((h, p.headers[h]))
        if p.content_type.is_delivery_status():
            collected += collect_from_status(p.body)
    return MimeHeaders(collected)


def collect_from_status(body):
    out = deque()
    with closing(StringIO(body)) as stream:
        for i in xrange(3):
            out += parse_stream(stream)
    return out


def get_status(headers):
    for v in headers.getall('Status'):
        if RE_STATUS.match(v.strip()):
            return v

def get_notification(message):
    for part in message.walk():
        if part.headers.get('Content-Description', '').lower() == 'notification':
            return part.body


HEADERS = ('Action',
           'Content-Description',
           'Diagnostic-Code',
           'Final-Recipient',
           'Received',
           'Remote-Mta',
           'Reporting-Mta',
           'Status')

RE_STATUS = re.compile(r'\d\.\d+\.\d+', re.IGNORECASE)

class Result(object):
    def __init__(self, score, status, notification, diagnostic_code):
        self.score = score
        self.status = status
        self.notification = notification
        self.diagnostic_code = diagnostic_code


