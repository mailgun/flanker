from nose.tools import eq_

from flanker.mime.message.headers.wrappers import ContentType

def charset_test():
    c = ContentType('text', 'plain')
    eq_('ascii', c.get_charset())

    c = ContentType('application', 'pdf')
    eq_(None, c.get_charset())
