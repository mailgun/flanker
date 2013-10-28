# coding:utf-8

from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from flanker.addresslib import address
from flanker.addresslib.address import EmailAddress
from flanker.addresslib.parser import ParserException

VALID_QTEXT         = [chr(x) for x in [0x21] + range(0x23, 0x5b) + range(0x5d, 0x7e)]
VALID_QUOTED_PAIR   = [chr(x) for x in range(0x20, 0x7e)]
INVALID_QTEXT       = [chr(x) for x in range(0x0, 0x8) + range(0xe, 0x1f) + [0x22, 0x5c, 0x7f]]
INVALID_QUOTED_PAIR = [chr(x) for x in range(0x0, 0x8) + range(0xe, 0x1f) + [0x7f]]

FULL_QTEXT = ''.join(VALID_QTEXT)
FULL_QUOTED_PAIR = '\\' + '\\'.join(VALID_QUOTED_PAIR)

@nottest
def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

@nottest
def run_full_mailbox_test(string, expected, full_spec=None):
    mbox = address.parse(string)
    if mbox:
        assert_equal(mbox.display_name, expected.display_name)
        assert_equal(mbox.address, expected.address)
        if full_spec:
            assert_equal(mbox.full_spec(), full_spec)
        return
    assert_equal(mbox, expected)

@nottest
def run_mailbox_test(string, expected_string):
    mbox = address.parse(string)
    if mbox:
        assert_equal(mbox.address, expected_string)
        return
    assert_equal(mbox, expected_string)


def test_mailbox():
    "Grammar: mailbox -> name-addr | addr-spec"

    # sanity
    run_full_mailbox_test('Steve Jobs <steve@apple.com>', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('"Steve Jobs" <steve@apple.com>', EmailAddress('"Steve Jobs"', 'steve@apple.com'))
    run_mailbox_test('<steve@apple.com>', 'steve@apple.com')

    run_full_mailbox_test('Steve Jobs steve@apple.com', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('"Steve Jobs" steve@apple.com', EmailAddress('"Steve Jobs"', 'steve@apple.com'))
    run_mailbox_test('steve@apple.com', 'steve@apple.com')


def test_name_addr():
    "Grammar: name-addr -> [ display-name ] angle-addr"

    # sanity
    run_full_mailbox_test('Linus Torvalds linus@kernel.org', EmailAddress('Linus Torvalds','linus@kernel.org'))
    run_full_mailbox_test('Linus Torvalds <linus@kernel.org>', EmailAddress('Linus Torvalds','linus@kernel.org'))
    run_mailbox_test('Linus Torvalds', None)
    run_mailbox_test('Linus Torvalds <>', None)
    run_mailbox_test('linus@kernel.org', 'linus@kernel.org')
    run_mailbox_test('<linus@kernel.org>', 'linus@kernel.org')
    try:
        run_mailbox_test(' ', None)
    except ParserException:
        pass


def test_display_name():
    "Grammar: display-name -> word { [ whitespace ] word }"

    # pass atom display-name rfc
    run_full_mailbox_test('ABCDEFGHIJKLMNOPQRSTUVWXYZ <a@b>', EmailAddress('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'a@b'))
    run_full_mailbox_test('abcdefghijklmnopqrstuvwzyz <a@b>', EmailAddress('abcdefghijklmnopqrstuvwzyz', 'a@b'))
    run_full_mailbox_test('0123456789 <a@b>', EmailAddress('0123456789', 'a@b'))
    run_full_mailbox_test('!#$%&\'*+-/=?^_`{|}~ <a@b>', EmailAddress('!#$%&\'*+-/=?^_`{|}~', 'a@b'))
    run_full_mailbox_test('Bill <bill@microsoft.com>', EmailAddress('Bill', 'bill@microsoft.com'))
    run_full_mailbox_test('Bill Gates <bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill  Gates <bill@microsoft.com>', EmailAddress('Bill  Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill Gates <bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test('Bill Gates<bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill Gates<bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill<bill@microsoft.com>', EmailAddress('Bill', 'bill@microsoft.com'))

    # pass atom display-name lax
    run_full_mailbox_test('ABCDEFGHIJKLMNOPQRSTUVWXYZ a@b', EmailAddress('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'a@b'))
    run_full_mailbox_test('abcdefghijklmnopqrstuvwzyz a@b', EmailAddress('abcdefghijklmnopqrstuvwzyz', 'a@b'))
    run_full_mailbox_test('0123456789 a@b', EmailAddress('0123456789', 'a@b'))
    run_full_mailbox_test('!#$%&\'*+-/=?^_`{|}~ a@b', EmailAddress('!#$%&\'*+-/=?^_`{|}~', 'a@b'))
    run_full_mailbox_test('Bill bill@microsoft.com', EmailAddress('Bill', 'bill@microsoft.com'))
    run_full_mailbox_test('Bill Gates bill@microsoft.com', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill  Gates bill@microsoft.com', EmailAddress('Bill  Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill Gates bill@microsoft.com', EmailAddress('Bill Gates', 'bill@microsoft.com'))


    # fail atom display-name rfc
    run_full_mailbox_test('@ <bill@microsoft.com>', None)
    run_full_mailbox_test('@ bill <bill@microsoft.com>', None)
    run_full_mailbox_test(' @ bill <bill@microsoft.com>', None)

    # fail atom display-name lax
    run_full_mailbox_test('@ bill@microsoft.com', None)
    run_full_mailbox_test('@ bill bill@microsoft.com', None)
    run_full_mailbox_test(' @ bill @microsoft.com', None)


    # pass display-name quoted-string rfc
    run_full_mailbox_test('"{}" <a@b>'.format(FULL_QTEXT), EmailAddress('"' + FULL_QTEXT + '"', 'a@b'))
    run_full_mailbox_test('"{}" <a@b>'.format(FULL_QUOTED_PAIR), EmailAddress('"' + FULL_QUOTED_PAIR + '"', 'a@b'))
    run_full_mailbox_test('"<a@b>" <a@b>', EmailAddress('"<a@b>"', 'a@b'))
    run_full_mailbox_test('"Bill" <bill@microsoft.com>', EmailAddress('"Bill"', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates" <bill@microsoft.com>', EmailAddress('"Bill Gates"', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates" <bill@microsoft.com>', EmailAddress('" Bill Gates"', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates " <bill@microsoft.com>', EmailAddress('"Bill Gates "', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates " <bill@microsoft.com>', EmailAddress('" Bill Gates "', 'bill@microsoft.com'))
    run_full_mailbox_test(' " Bill Gates "<bill@microsoft.com>', EmailAddress('" Bill Gates "', 'bill@microsoft.com'))

    # fail display-name quoted-string rfc
    run_mailbox_test('"{} <a@b>"'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('"{} <a@b>'.format(FULL_QTEXT), None)
    run_mailbox_test('{}" <a@b>'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('{} <a@b>'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('"{}" <a@b>'.format(''.join(INVALID_QTEXT)), None)
    run_mailbox_test('"{}" <a@b>'.format('\\' + '\\'.join(INVALID_QUOTED_PAIR)), None)
    for invalid_char in INVALID_QTEXT:
        run_mailbox_test('"{}" <a@b>'.format(invalid_char), None)
    for invalid_char in INVALID_QUOTED_PAIR:
        run_mailbox_test('"{}" <a@b>'.format('\\' + invalid_char), None)


    # pass display-name quoted-string lax
    run_full_mailbox_test('"{}" a@b'.format(FULL_QTEXT), EmailAddress('"' + FULL_QTEXT + '"', 'a@b'))
    run_full_mailbox_test('"{}" a@b'.format(FULL_QUOTED_PAIR), EmailAddress('"' + FULL_QUOTED_PAIR + '"', 'a@b'))
    run_full_mailbox_test('"a@b" a@b', EmailAddress('"a@b"', 'a@b'))
    run_full_mailbox_test('"Bill" bill@microsoft.com', EmailAddress('"Bill"', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates" bill@microsoft.com', EmailAddress('"Bill Gates"', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates" bill@microsoft.com', EmailAddress('" Bill Gates"', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates " bill@microsoft.com', EmailAddress('"Bill Gates "', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates " bill@microsoft.com', EmailAddress('" Bill Gates "', 'bill@microsoft.com'))

    # fail display-name quoted-string lax
    #from pudb import set_trace; set_trace()
    run_mailbox_test('"Bill Gates"bill@microsoft.com', None)
    run_mailbox_test('"{} a@b"'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('"{} a@b'.format(FULL_QTEXT), None)
    run_mailbox_test('{}" a@b'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('{} a@b'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('"{}" a@b'.format(''.join(INVALID_QTEXT)), None)
    run_mailbox_test('"{}" a@b'.format('\\' + '\\'.join(INVALID_QUOTED_PAIR)), None)
    for invalid_char in INVALID_QTEXT:
        run_mailbox_test('"{}" a@b'.format(invalid_char), None)
    for invalid_char in INVALID_QUOTED_PAIR:
        run_mailbox_test('"{}" a@b'.format('\\' + invalid_char), None)

    # pass unicode display-name sanity
    run_full_mailbox_test(u'Bill <bill@microsoft.com>', EmailAddress(u'Bill', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐill <bill@microsoft.com>', EmailAddress(u'ϐill', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐΙλλ <bill@microsoft.com>', EmailAddress(u'ϐΙλλ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐΙλλ Γαθεσ <bill@microsoft.com>', EmailAddress(u'ϐΙλλ Γαθεσ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'BΙλλ Γαθεσ <bill@microsoft.com>', EmailAddress(u'BΙλλ Γαθεσ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'Bill Γαθεσ <bill@microsoft.com>', EmailAddress(u'Bill Γαθεσ', 'bill@microsoft.com'))

    # fail unicode display-name, sanity
    run_mailbox_test('ϐΙλλ Γαθεσ <bill@microsoft.com>', None)


def test_unicode_display_name():
    # unicode, no quotes, display-name rfc
    run_full_mailbox_test(u'ö <{}>'.format(u'foo@example.com'),
        EmailAddress(u'ö', 'foo@example.com'), '=?utf-8?b?w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Föö <{}>'.format(u'foo@example.com'),
        EmailAddress(u'Föö', 'foo@example.com'), '=?utf-8?b?RsO2w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Foo ö <{}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo ö', 'foo@example.com'), '=?utf-8?b?Rm9vIMO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö <{}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo <{}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo Föö <{}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?= <foo@example.com>')

    # unicode, no quotes, display-name lax
    run_full_mailbox_test(u'ö {}'.format(u'foo@example.com'),
        EmailAddress(u'ö', 'foo@example.com'), '=?utf-8?b?w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Föö {}'.format(u'foo@example.com'),
        EmailAddress(u'Föö', 'foo@example.com'), '=?utf-8?b?RsO2w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Foo ö {}'.format(u'foo@example.com'),
        EmailAddress(u'Foo ö', 'foo@example.com'), '=?utf-8?b?Rm9vIMO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö {}'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo {}'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo Föö {}'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?= <foo@example.com>')


    # unicode, quotes, display-name rfc
    run_full_mailbox_test(u'"ö" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"ö"', 'foo@example.com'), '"=?utf-8?b?w7Y=?=" <foo@example.com>')
    run_full_mailbox_test(u'"Föö" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"Föö"', 'foo@example.com'), '"=?utf-8?b?RsO2w7Y=?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo ö" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"Foo ö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIMO2?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö Foo" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö Foo"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö Foo Föö" <{}>'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö Foo Föö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?=" <foo@example.com>')

    # unicode, quotes, display-name lax
    run_full_mailbox_test(u'"ö" {}'.format(u'foo@example.com'),
        EmailAddress(u'"ö"', 'foo@example.com'), '"=?utf-8?b?w7Y=?=" <foo@example.com>')
    run_full_mailbox_test(u'"Föö" {}'.format(u'foo@example.com'),
        EmailAddress(u'"Föö"', 'foo@example.com'), '"=?utf-8?b?RsO2w7Y=?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo ö" {}'.format(u'foo@example.com'),
        EmailAddress(u'"Foo ö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIMO2?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö" {}'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö Foo" {}'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö Foo"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?=" <foo@example.com>')
    run_full_mailbox_test(u'"Foo Föö Foo Föö" {}'.format(u'foo@example.com'),
        EmailAddress(u'"Foo Föö Foo Föö"', 'foo@example.com'), '"=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?=" <foo@example.com>')


    # unicode, random language sampling, see: http://www.columbia.edu/~fdc/utf8/index.html
    run_full_mailbox_test(u'나는 유리를 먹을 수 있어요 <foo@example.com>',
        EmailAddress(u'나는 유리를 먹을 수 있어요', 'foo@example.com'),
        '=?utf-8?b?64KY64qUIOycoOumrOulvCDrqLnsnYQg7IiYIOyeiOyWtOyalA==?= <foo@example.com>')
    run_full_mailbox_test(u'私はガラスを食べられます <foo@example.com>',
        EmailAddress(u'私はガラスを食べられます', 'foo@example.com'),
        '=?utf-8?b?56eB44Gv44Ks44Op44K544KS6aOf44G544KJ44KM44G+44GZ?= <foo@example.com>')
    run_full_mailbox_test(u'ᛖᚴ ᚷᛖᛏ ᛖᛏᛁ <foo@example.com>',
        EmailAddress(u'ᛖᚴ ᚷᛖᛏ ᛖᛏᛁ', 'foo@example.com'),
        '=?utf-8?b?4ZuW4Zq0IOGat+GbluGbjyDhm5bhm4/hm4E=?= <foo@example.com>')
    run_full_mailbox_test(u'Falsches Üben von Xylophonmusik <foo@example.com>',
        EmailAddress(u'Falsches Üben von Xylophonmusik', 'foo@example.com'),
        '=?utf-8?q?Falsches_=C3=9Cben_von_Xylophonmusik?= <foo@example.com>')
    run_full_mailbox_test(u'Съешь же ещё этих <foo@example.com>',
        EmailAddress(u'Съешь же ещё этих', 'foo@example.com'),
        '=?utf-8?b?0KHRitC10YjRjCDQttC1INC10YnRkSDRjdGC0LjRhQ==?= <foo@example.com>')
    run_full_mailbox_test(u'ξεσκεπάζω την <foo@example.com>',
        EmailAddress(u'ξεσκεπάζω την', 'foo@example.com'),
        '=?utf-8?b?zr7Otc+DzrrOtc+AzqzOts+JIM+EzrfOvQ==?= <foo@example.com>')


def test_angle_addr():
    "Grammar: angle-addr -> [ whitespace ] < addr-spec > [ whitespace ]"

    # pass angle-addr
    run_mailbox_test('<steve@apple.com>', 'steve@apple.com')
    run_full_mailbox_test('Steve Jobs <steve@apple.com>', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('Steve Jobs < steve@apple.com>', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('Steve Jobs <steve@apple.com >', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('Steve Jobs < steve@apple.com >', EmailAddress('Steve Jobs', 'steve@apple.com'))

    # fail angle-addr
    run_full_mailbox_test('<steve@apple.com', None)
    run_full_mailbox_test('Steve Jobs steve@apple.com>', None)
    run_full_mailbox_test('steve@apple.com>', None)
    run_full_mailbox_test('Steve Jobs <steve@apple.com', None)
    run_full_mailbox_test('Steve Jobs <@steve@apple.com>', None)
    run_full_mailbox_test('<Steve Jobs <steve@apple.com>>', None)
    run_full_mailbox_test('<Steve Jobs <steve@apple.com>', None)
    run_full_mailbox_test('Steve Jobs <steve@apple.com>>', None)
    run_full_mailbox_test('<Steve Jobs> <steve@apple.com>', None)
    run_full_mailbox_test('<Steve Jobs <steve@apple.com>', None)
    run_full_mailbox_test('Steve Jobs> <steve@apple.com>', None)
    run_full_mailbox_test('Steve Jobs <<steve@apple.com>>', None)
    run_full_mailbox_test('Steve Jobs <<steve@apple.com>', None)


def test_addr_spec():
    "Grammar: addr-spec -> [ whitespace ] local-part @ domain [ whitespace ]"

    # pass addr-spec
    run_mailbox_test('linus@kernel.org', 'linus@kernel.org')
    run_mailbox_test(' linus@kernel.org', 'linus@kernel.org')
    run_mailbox_test('linus@kernel.org ', 'linus@kernel.org')
    run_mailbox_test(' linus@kernel.org ', 'linus@kernel.org')
    run_mailbox_test('linus@localhost', 'linus@localhost')

    # fail addr-spec
    run_mailbox_test('linus@', None)
    run_mailbox_test('linus@ ', None)
    run_mailbox_test('linus@;', None)
    run_mailbox_test('linus@@kernel.org', None)
    run_mailbox_test('linus@ @kernel.org', None)
    run_mailbox_test('linus@ @localhost', None)
    run_mailbox_test('linus-at-kernel.org', None)
    run_mailbox_test('linus at kernel.org', None)
    run_mailbox_test('linus kernel.org', None)


def test_local_part():
    "Grammar: local-part -> dot-atom | quoted-string"

    # test length limits
    run_mailbox_test(''.join(['a'*128, '@b']), ''.join(['a'*128, '@b']))
    run_mailbox_test(''.join(['a'*129, '@b']), None)

    # because qtext and quoted-pair are longer than 64 bytes (limit on local-part)
    # we use a sample in testing, every other for qtext and every fifth for quoted-pair
    sample_qtext = FULL_QTEXT[::2]
    sample_qpair = FULL_QUOTED_PAIR[::5]

    # pass dot-atom
    run_mailbox_test('ABCDEFGHIJKLMNOPQRSTUVWXYZ@apple.com', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ@apple.com')
    run_mailbox_test('abcdefghijklmnopqrstuvwzyz@apple.com', 'abcdefghijklmnopqrstuvwzyz@apple.com')
    run_mailbox_test('0123456789@apple.com', '0123456789@apple.com')
    run_mailbox_test('!#$%&\'*+-/=?^_`{|}~@apple.com', '!#$%&\'*+-/=?^_`{|}~@apple.com')
    run_mailbox_test('AZaz09!#$%&\'*+-/=?^_`{|}~@apple.com', 'AZaz09!#$%&\'*+-/=?^_`{|}~@apple.com')
    run_mailbox_test('steve@apple.com', 'steve@apple.com')
    run_mailbox_test(' steve@apple.com', 'steve@apple.com')
    run_mailbox_test('  steve@apple.com', 'steve@apple.com')

    # fail dot-atom
    run_mailbox_test('steve @apple.com', None)
    run_mailbox_test(' steve @apple.com', None)
    run_mailbox_test(', steve@apple.com', None)
    run_mailbox_test(';;steve@apple.com', None)
    run_mailbox_test('"steve@apple.com', None)
    run_mailbox_test('steve"@apple.com', None)
    run_mailbox_test('steve jobs @apple.com', None)
    run_mailbox_test(' steve jobs @apple.com', None)
    run_mailbox_test('steve..jobs@apple.com', None)

    # pass qtext
    for cnk in chunks(FULL_QTEXT, len(FULL_QTEXT)/2):
        run_mailbox_test('"{}"@b'.format(cnk), '"{}"@b'.format(cnk))
    run_mailbox_test('" {}"@b'.format(sample_qtext), '" {}"@b'.format(sample_qtext))
    run_mailbox_test('"{} "@b'.format(sample_qtext), '"{} "@b'.format(sample_qtext))
    run_mailbox_test('" {} "@b'.format(sample_qtext), '" {} "@b'.format(sample_qtext))
    run_full_mailbox_test('"{0}" "{0}"@b'.format(sample_qtext),
        EmailAddress('"{}"'.format(sample_qtext), '"{}"@b'.format(sample_qtext)))

    # fail qtext
    run_mailbox_test('"{0}""{0}"@b'.format(sample_qtext), None)
    run_mailbox_test('"john""smith"@b'.format(sample_qtext), None)
    run_mailbox_test('"{}" @b'.format(sample_qtext), None)
    run_mailbox_test(' "{}" @b'.format(sample_qtext), None)
    run_mailbox_test('"{}@b'.format(sample_qtext), None)
    run_mailbox_test('{}"@b'.format(sample_qtext), None)
    run_mailbox_test('{}@b'.format(sample_qtext), None)
    run_mailbox_test('"{}@b"'.format(sample_qtext), None)
    run_mailbox_test('"{}"@b'.format(''.join(INVALID_QTEXT)), None)
    for invalid_char in INVALID_QTEXT:
        run_mailbox_test('"{}"@b'.format(invalid_char), None)

    # pass quoted-pair
    for cnk in chunks(FULL_QUOTED_PAIR, len(FULL_QUOTED_PAIR)/3):
        run_mailbox_test('"{}"@b'.format(cnk), '"{}"@b'.format(cnk))
    run_mailbox_test('" {}"@b'.format(sample_qpair), '" {}"@b'.format(sample_qpair))
    run_mailbox_test('"{} "@b'.format(sample_qpair), '"{} "@b'.format(sample_qpair))
    run_mailbox_test('" {} "@b'.format(sample_qpair), '" {} "@b'.format(sample_qpair))
    run_full_mailbox_test('"{0}" "{0}"@b'.format(sample_qpair),
        EmailAddress('"{}"'.format(sample_qpair), '"{}"@b'.format(sample_qpair)))

    # fail quoted-pair
    run_mailbox_test('"{0}""{0}"@b'.format(sample_qpair), None)
    run_mailbox_test('"john""smith"@b'.format(sample_qpair), None)
    run_mailbox_test('"{}" @b'.format(sample_qpair), None)
    run_mailbox_test(' "{}" @b'.format(sample_qpair), None)
    run_mailbox_test('"{}@b'.format(sample_qpair), None)
    run_mailbox_test('{}"@b'.format(sample_qpair), None)
    run_mailbox_test('{}@b'.format(sample_qpair), None)
    run_mailbox_test('"{}@b"'.format(sample_qpair), None)
    run_mailbox_test('"{}"@b'.format(''.join(INVALID_QUOTED_PAIR)), None)
    for invalid_char in INVALID_QUOTED_PAIR:
        run_mailbox_test('"{}"@b'.format(invalid_char), None)


def test_domain():
    "Grammar: domain -> dot-atom"

    # test length limits
    max_domain_len = ''.join(['a'*62, '.', 'b'*62, '.', 'c'*63, '.', 'd'*63])
    overlimit_domain_one = ''.join(['a'*62, '.', 'b'*62, '.', 'c'*63, '.', 'd'*64])
    overlimit_domain_two = ''.join(['a'*62, '.', 'b'*62, '.', 'c'*63, '.', 'd'*63, '.', 'a'])
    run_mailbox_test(''.join(['b@', 'a'*63]), ''.join(['b@', 'a'*63]))
    run_mailbox_test(''.join(['b@', 'a'*64]), None)
    run_mailbox_test(''.join(['a@', max_domain_len]), ''.join(['a@', max_domain_len]))
    run_mailbox_test(''.join(['a@', overlimit_domain_one]), None)
    run_mailbox_test(''.join(['a@', overlimit_domain_two]), None)


    # pass dot-atom
    run_mailbox_test('bill@ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'bill@abcdefghijklmnopqrstuvwxyz')
    run_mailbox_test('bill@abcdefghijklmnopqrstuvwxyz', 'bill@abcdefghijklmnopqrstuvwxyz')
    run_mailbox_test('bill@0123456789', 'bill@0123456789')
    run_mailbox_test('bill@!#$%&\'*+-/=?^_`{|}~', 'bill@!#$%&\'*+-/=?^_`{|}~')
    run_mailbox_test('bill@microsoft.com', 'bill@microsoft.com')
    run_mailbox_test('bill@retired.microsoft.com', 'bill@retired.microsoft.com')
    run_mailbox_test('bill@microsoft.com ', 'bill@microsoft.com')
    run_mailbox_test('bill@microsoft.com  ', 'bill@microsoft.com')

    # fail dot-atom
    run_mailbox_test('bill@micro soft.com', None)
    run_mailbox_test('bill@micro. soft.com', None)
    run_mailbox_test('bill@micro .soft.com', None)
    run_mailbox_test('bill@micro. .soft.com', None)
    run_mailbox_test('bill@microsoft.com,', None)
    run_mailbox_test('bill@microsoft.com, ', None)
    run_mailbox_test('bill@microsoft.com, ', None)
    run_mailbox_test('bill@microsoft.com , ', None)
    run_mailbox_test('bill@microsoft.com,,', None)
    run_mailbox_test('bill@microsoft.com.', None)
    run_mailbox_test('bill@microsoft.com..', None)
    run_mailbox_test('bill@microsoft..com', None)
    run_mailbox_test('bill@retired.microsoft..com', None)
    run_mailbox_test('bill@.com', None)
    run_mailbox_test('bill@.com.', None)
    run_mailbox_test('bill@.microsoft.com', None)
    run_mailbox_test('bill@.microsoft.com.', None)
    run_mailbox_test('bill@"microsoft.com"', None)
    run_mailbox_test('bill@"microsoft.com', None)
    run_mailbox_test('bill@microsoft.com"', None)
