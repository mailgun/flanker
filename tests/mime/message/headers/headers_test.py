# coding:utf-8

import zlib

from nose.tools import *
from mock import *
from flanker.mime.message.headers import MimeHeaders
from flanker.mime.message.errors import DecodingError
from cStringIO import StringIO

from .... import *

def headers_case_insensitivity_test():
    h = MimeHeaders()
    h['Content-Type'] = 1
    eq_(1, h['Content-Type'])
    eq_(1, h['conTenT-TyPE'])
    ok_('cOnTenT-TyPE' in h)
    ok_('Content-Type' in h)
    eq_(1, h.get('Content-Type'))
    eq_(None, h.get('Content-Type2'))
    eq_([('Content-Type', 1)], h.items())


def headers_order_preserved_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)

    # various types of iterations
    should_be = [('Mime-Version', '1'), ('Received', '2'), ('Mime-Version', '3'), ('Received', '4')]
    eq_(should_be, h.items())
    ok_(isinstance(h.items(), list))
    eq_(should_be, [p for p in h.iteritems()])

    # iterate over keys
    keys = ['Mime-Version', 'Received', 'Mime-Version', 'Received']
    eq_(keys, [p for p in h])
    eq_(keys, h.keys())


def headers_boolean_test():
    eq_(False, bool(MimeHeaders()))
    eq_(True, bool(MimeHeaders([('A', 1)])))

def headers_to_string_test():
    ok_(str(MimeHeaders([('A', 1)])))


def headers_multiple_values_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)
    eq_(['1', '3'], h.getall('Mime-Version'))

    # set re-sets all values for the message
    h['Mime-Version'] = '5'
    eq_(['5'], h.getall('Mime-Version'))

    # use add to add more values
    h.add('Received', '6')
    eq_(['2', '4', '6'], h.getall('Received'))

    # use prepend to insert header in the begining of the list
    h.prepend('Received', '0')
    eq_(['0', '2', '4', '6'], h.getall('Received'))

    # delete removes it all!
    del h['RECEIVED']
    eq_([], h.getall('Received'))


def headers_length_test():
    h = MimeHeaders()
    eq_(0, len(h))

    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]
    h = MimeHeaders(headers)
    eq_(4, len(h))


def headers_alternation_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]

    h = MimeHeaders(headers)
    assert_false(h.have_changed())

    h.prepend('Received', 'Yo')
    ok_(h.have_changed())

    h = MimeHeaders(headers)
    del h['Mime-Version']
    ok_(h.have_changed())

    h = MimeHeaders(headers)
    h['Mime-Version'] = 'a'
    ok_(h.have_changed())

    h = MimeHeaders(headers)
    h.add('Mime-Version', 'a')
    ok_(h.have_changed())

    h = MimeHeaders(headers)
    h.getall('Mime-Version')
    h.get('o')
    assert_false(h.have_changed())


def headers_transform_test():
    headers = [('mime-version', '1'), ('rEceived', '2'), ('mime-version', '3'), ('ReceiveD', '4')]

    h = MimeHeaders(headers)

    # transform tracks whether anything actually changed
    h.transform(lambda key,val: (key, val))
    assert_false(h.have_changed())

    # ok, now something have changed, make sure we've preserved order and did not collapse anything
    h.transform(lambda key,val: ("X-{0}".format(key), "t({0})".format(val)))
    ok_(h.have_changed())

    eq_([('X-Mime-Version', 't(1)'), ('X-Received', 't(2)'), ('X-Mime-Version', 't(3)'), ('X-Received', 't(4)')], h.items())


def headers_parsing_empty_test():
    h = MimeHeaders.from_stream(StringIO(""))
    eq_(0, len(h))

def headers_parsing_ridiculously_long_line_test():
    val = "abcdefg"*100000
    header = "Hello: {0}\r\n".format(val)
    assert_raises(
        DecodingError, MimeHeaders.from_stream, StringIO(header))


def headers_parsing_binary_stuff_survives_test():
    value = zlib.compress("abcdefg")
    header = "Hello: {0}\r\n".format(value)
    assert_raises(
        DecodingError, MimeHeaders.from_stream, StringIO(header))


def broken_sequences_test():
    headers = StringIO("  hello this is a bad header\nGood: this one is ok")
    headers = MimeHeaders.from_stream(headers)
    eq_(1, len(headers))
    eq_("this one is ok", headers["Good"])


def bilingual_message_test():
    headers = MimeHeaders.from_stream(StringIO(BILINGUAL))
    eq_(21, len(headers))
    eq_(u"Simple text. How are you? Как ты поживаешь?", headers['Subject'])
    received_headers = headers.getall('Received')
    eq_(5, len(received_headers))
    ok_('c2cs24435ybk' in received_headers[0])


def headers_roundtrip_test():
    headers = MimeHeaders.from_stream(StringIO(BILINGUAL))
    out = StringIO()
    headers.to_stream(out)

    headers2 = MimeHeaders.from_stream(StringIO(out.getvalue()))
    eq_(21, len(headers2))
    eq_(u"Simple text. How are you? Как ты поживаешь?", headers['Subject'])
    received_headers = headers.getall('Received')
    eq_(5, len(received_headers))
    ok_('c2cs24435ybk' in received_headers[0])
    eq_(headers['Content-Transfer-Encoding'],
        headers2['Content-Transfer-Encoding'])
    eq_(headers['DKIM-Signature'],
        headers2['DKIM-Signature'])


def test_folding_combinations():
    message = """From mrc@example.com Mon Feb  8 02:53:47 PST 1993\nTo: sasha\r\n  continued\n      line\nFrom: single line  \r\nSubject: hello, how are you\r\n today?"""
    headers = MimeHeaders.from_stream(StringIO(message))
    eq_('sasha  continued      line', headers['To'])
    eq_('single line  ', headers['From'])
    eq_("hello, how are you today?", headers['Subject'])
