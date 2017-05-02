# coding:utf-8

from nose.tools import nottest, assert_equal, assert_not_equal

from flanker.addresslib import address
from flanker.addresslib.address import EmailAddress
from ply.lex import LexError
from ply.yacc import YaccError

VALID_QTEXT         = [chr(x) for x in [0x21] + range(0x23, 0x5b) + range(0x5d, 0x7e)]
VALID_QUOTED_PAIR   = [chr(x) for x in range(0x20, 0x7e)]

FULL_QTEXT = ''.join(VALID_QTEXT)
FULL_QUOTED_PAIR = '\\' + '\\'.join(VALID_QUOTED_PAIR)

CONTROL_CHARS = ''.join(map(unichr, range(0, 9) + range(14, 32) + [127] ))

@nottest
def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

@nottest
def run_full_mailbox_test(string, expected, full_spec=None):
    mbox = address.parse(string)
    if mbox:
        assert_equal(expected.display_name, mbox.display_name)
        assert_equal(expected.address, mbox.address)
        if full_spec:
            assert_equal(full_spec, mbox.full_spec())
        assert_equal(mbox, address.parse(mbox.to_unicode())) # check symmetry
        return
    assert_equal(expected, mbox)

@nottest
def run_mailbox_test(string, expected_string):
    mbox = address.parse(string)
    if mbox:
        assert_equal(expected_string, mbox.address)
        return
    assert_equal(expected_string, mbox)


def test_mailbox():
    "Grammar: mailbox -> name-addr | addr-spec"

    # sanity
    run_full_mailbox_test('Steve Jobs <steve@apple.com>', EmailAddress('Steve Jobs', 'steve@apple.com'))
    run_full_mailbox_test('"Steve Jobs" <steve@apple.com>', EmailAddress('Steve Jobs', 'steve@apple.com'))

    run_mailbox_test('steve@apple.com', 'steve@apple.com')


def test_name_addr():
    "Grammar: name-addr -> [ display-name ] angle-addr"

    # sanity
    run_full_mailbox_test('Linus Torvalds <linus@kernel.org>', EmailAddress('Linus Torvalds','linus@kernel.org'))
    run_mailbox_test('Linus Torvalds', None)
    run_mailbox_test('Linus Torvalds <>', None)
    run_mailbox_test('linus@kernel.org', 'linus@kernel.org')
    try:
        run_mailbox_test(' ', None)
    except LexError:
        pass
    except YaccError:
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
    run_full_mailbox_test(' Bill  Gates <bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill Gates <bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test('Bill Gates<bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill Gates<bill@microsoft.com>', EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test(' Bill<bill@microsoft.com>', EmailAddress('Bill', 'bill@microsoft.com'))

    # fail atom display-name rfc
    run_full_mailbox_test('< <bill@microsoft.com>', None)
    run_full_mailbox_test('< bill <bill@microsoft.com>', None)
    run_full_mailbox_test(' < bill <bill@microsoft.com>', None)

    # pass display-name quoted-string rfc
    run_full_mailbox_test('"{0}" <a@b>'.format(FULL_QTEXT),
                          EmailAddress(FULL_QTEXT, 'a@b'))
    run_full_mailbox_test('"{0}" <a@b>'.format(FULL_QUOTED_PAIR),
                          EmailAddress(''.join(VALID_QUOTED_PAIR), 'a@b'))
    run_full_mailbox_test('"<a@b>" <a@b>', EmailAddress('<a@b>', 'a@b'))
    run_full_mailbox_test('"Bill" <bill@microsoft.com>',
                          EmailAddress('Bill', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates" <bill@microsoft.com>',
                          EmailAddress('Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates" <bill@microsoft.com>',
                          EmailAddress(' Bill Gates', 'bill@microsoft.com'))
    run_full_mailbox_test('"Bill Gates " <bill@microsoft.com>',
                          EmailAddress('Bill Gates ', 'bill@microsoft.com'))
    run_full_mailbox_test('" Bill Gates " <bill@microsoft.com>',
                          EmailAddress(' Bill Gates ', 'bill@microsoft.com'))
    run_full_mailbox_test(' " Bill Gates "<bill@microsoft.com>',
                          EmailAddress(' Bill Gates ', 'bill@microsoft.com'))

    # fail display-name quoted-string rfc
    run_mailbox_test('"{0} <a@b>"'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('"{0} <a@b>'.format(FULL_QTEXT), None)
    run_mailbox_test('{0}" <a@b>'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test('{0} <a@b>'.format(FULL_QUOTED_PAIR), None)
    run_mailbox_test(u'{0} <a@b>'.format(''.join(CONTROL_CHARS)), None)
    run_mailbox_test(u'"{0}" <a@b>'.format(''.join(CONTROL_CHARS)), None)
    for cc in CONTROL_CHARS:
        run_mailbox_test(u'"{0}" <a@b>'.format(cc), None)
        run_mailbox_test(u'{0} <a@b>'.format(cc), None)

    # pass unicode display-name sanity
    run_full_mailbox_test(u'Bill <bill@microsoft.com>', EmailAddress(u'Bill', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐill <bill@microsoft.com>', EmailAddress(u'ϐill', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐΙλλ <bill@microsoft.com>', EmailAddress(u'ϐΙλλ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'ϐΙλλ Γαθεσ <bill@microsoft.com>', EmailAddress(u'ϐΙλλ Γαθεσ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'BΙλλ Γαθεσ <bill@microsoft.com>', EmailAddress(u'BΙλλ Γαθεσ', 'bill@microsoft.com'))
    run_full_mailbox_test(u'Bill Γαθεσ <bill@microsoft.com>', EmailAddress(u'Bill Γαθεσ', 'bill@microsoft.com'))

    # period in display name
    run_full_mailbox_test(u'Bill. Gates. <bill@microsoft.com>', EmailAddress(u'Bill. Gates.', 'bill@microsoft.com'))


def test_unicode_display_name():
    # unicode, no quotes, display-name rfc
    run_full_mailbox_test(u'ö <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'ö', 'foo@example.com'), '=?utf-8?b?w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Föö <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'Föö', 'foo@example.com'), '=?utf-8?b?RsO2w7Y=?= <foo@example.com>')
    run_full_mailbox_test(u'Foo ö <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo ö', 'foo@example.com'), '=?utf-8?b?Rm9vIMO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?= <foo@example.com>')
    run_full_mailbox_test(u'Foo Föö Foo Föö <{0}>'.format(u'foo@example.com'),
        EmailAddress(u'Foo Föö Foo Föö', 'foo@example.com'), '=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?= <foo@example.com>')

    # unicode, quotes, display-name rfc
    # Note that redundant quotes are removed from the parsed address
    run_full_mailbox_test(
        u'"ö" <foo@example.com>',
        EmailAddress(u'ö', 'foo@example.com'),
        '=?utf-8?b?w7Y=?= <foo@example.com>')
    run_full_mailbox_test(
        u'"Föö" <foo@example.com>',
        EmailAddress(u'Föö', 'foo@example.com'),
        '=?utf-8?b?RsO2w7Y=?= <foo@example.com>')
    run_full_mailbox_test(
        u'"Foo ö" <foo@example.com>',
        EmailAddress(u'Foo ö', 'foo@example.com'),
        '=?utf-8?b?Rm9vIMO2?= <foo@example.com>')
    run_full_mailbox_test(
        u'"Foo Föö" <foo@example.com>',
        EmailAddress(u'Foo Föö', 'foo@example.com'),
        '=?utf-8?b?Rm9vIEbDtsO2?= <foo@example.com>')
    run_full_mailbox_test(
        u'"Foo Föö Foo" <foo@example.com>',
        EmailAddress(u'Foo Föö Foo', 'foo@example.com'),
        '=?utf-8?b?Rm9vIEbDtsO2IEZvbw==?= <foo@example.com>')
    run_full_mailbox_test(
        u'"Foo Föö Foo Föö" <foo@example.com>',
        EmailAddress(u'Foo Föö Foo Föö', 'foo@example.com'),
        '=?utf-8?b?Rm9vIEbDtsO2IEZvbyBGw7bDtg==?= <foo@example.com>')

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

    # unicode + punctuation
    for i in u'''.!#$%&*+-/=?^_`{|}~''':
        run_full_mailbox_test(u'"ö {0}" <foo@example.com>'.format(i),
            EmailAddress(u'ö {0}'.format(i), 'foo@example.com'))


def test_unicode_special_chars():
    # unicode, special chars, no quotes
    run_full_mailbox_test(u'foo © bar <foo@example.com>',
        EmailAddress(u'foo © bar', 'foo@example.com'),
        '=?utf-8?q?foo_=C2=A9_bar?= <foo@example.com>')
    run_full_mailbox_test(u'foo œ bar <foo@example.com>',
        EmailAddress(u'foo œ bar', 'foo@example.com'),
        '=?utf-8?q?foo_=C5=93_bar?= <foo@example.com>')
    run_full_mailbox_test(u'foo – bar <foo@example.com>',
        EmailAddress(u'foo – bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKAkyBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo Ǽ bar <foo@example.com>',
        EmailAddress(u'foo Ǽ bar', 'foo@example.com'),
        '=?utf-8?q?foo_=C7=BC_bar?= <foo@example.com>')
    run_full_mailbox_test(u'foo ₤ bar <foo@example.com>',
        EmailAddress(u'foo ₤ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKCpCBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo Ω bar <foo@example.com>',
        EmailAddress(u'foo Ω bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKEpiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ↵ bar <foo@example.com>',
        EmailAddress(u'foo ↵ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKGtSBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ∑ bar <foo@example.com>',
        EmailAddress(u'foo ∑ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKIkSBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ⏲ bar <foo@example.com>',
        EmailAddress(u'foo ⏲ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKPsiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo Ⓐ bar <foo@example.com>',
        EmailAddress(u'foo Ⓐ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKStiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ▒ bar <foo@example.com>',
        EmailAddress(u'foo ▒ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKWkiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ▲ bar <foo@example.com>',
        EmailAddress(u'foo ▲ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKWsiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ⚔ bar <foo@example.com>',
        EmailAddress(u'foo ⚔ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKalCBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ✎ bar <foo@example.com>',
        EmailAddress(u'foo ✎ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKcjiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ⠂ bar <foo@example.com>',
        EmailAddress(u'foo ⠂ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKggiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo ⬀ bar <foo@example.com>',
        EmailAddress(u'foo ⬀ bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKsgCBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'foo 💩 bar <foo@example.com>',
        EmailAddress(u'foo 💩 bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIPCfkqkgYmFy?= <foo@example.com>')

    # unicode, special chars, quotes
    # Note that quotes are removed from the parsed display name
    run_full_mailbox_test(u'"foo © bar" <foo@example.com>',
        EmailAddress(u'foo © bar', u'foo@example.com'),
        '=?utf-8?q?foo_=C2=A9_bar?= <foo@example.com>')
    run_full_mailbox_test(u'"foo œ bar" <foo@example.com>',
        EmailAddress(u'foo œ bar', u'foo@example.com'),
        '=?utf-8?q?foo_=C5=93_bar?= <foo@example.com>')
    run_full_mailbox_test(u'"foo – bar" <foo@example.com>',
        EmailAddress(u'foo – bar', 'foo@example.com'),
        '=?utf-8?b?Zm9vIOKAkyBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo Ǽ bar" <foo@example.com>',
        EmailAddress(u'foo Ǽ bar', u'foo@example.com'),
        '=?utf-8?q?foo_=C7=BC_bar?= <foo@example.com>')
    run_full_mailbox_test(u'"foo Ω bar" <foo@example.com>',
        EmailAddress(u'foo Ω bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKEpiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ↵ bar" <foo@example.com>',
        EmailAddress(u'foo ↵ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKGtSBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ∑ bar" <foo@example.com>',
        EmailAddress(u'foo ∑ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKIkSBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ⏲ bar" <foo@example.com>',
        EmailAddress(u'foo ⏲ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKPsiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo Ⓐ bar" <foo@example.com>',
        EmailAddress(u'foo Ⓐ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKStiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ▒ bar" <foo@example.com>',
        EmailAddress(u'foo ▒ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKWkiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ▲ bar" <foo@example.com>',
        EmailAddress(u'foo ▲ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKWsiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ⚔ bar" <foo@example.com>',
        EmailAddress(u'foo ⚔ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKalCBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ✎ bar" <foo@example.com>',
        EmailAddress(u'foo ✎ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKcjiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ⠂ bar" <foo@example.com>',
        EmailAddress(u'foo ⠂ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKggiBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo ⬀ bar" <foo@example.com>',
        EmailAddress(u'foo ⬀ bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIOKsgCBiYXI=?= <foo@example.com>')
    run_full_mailbox_test(u'"foo 💩 bar" <foo@example.com>',
        EmailAddress(u'foo 💩 bar', u'foo@example.com'),
        '=?utf-8?b?Zm9vIPCfkqkgYmFy?= <foo@example.com>')

    # unicode, language specific punctuation, just test with !
    run_full_mailbox_test(u'fooǃ <foo@example.com>',
        EmailAddress(u'fooǃ', u'foo@example.com'),
        '=?utf-8?b?Zm9vx4M=?= <foo@example.com>')
    run_full_mailbox_test(u'foo‼ <foo@example.com>',
        EmailAddress(u'foo‼', u'foo@example.com'),
        '=?utf-8?b?Zm9v4oC8?= <foo@example.com>')
    run_full_mailbox_test(u'foo⁈ <foo@example.com>',
        EmailAddress(u'foo⁈', u'foo@example.com'),
        '=?utf-8?b?Zm9v4oGI?= <foo@example.com>')
    run_full_mailbox_test(u'foo⁉ <foo@example.com>',
        EmailAddress(u'foo⁉', u'foo@example.com'),
        '=?utf-8?b?Zm9v4oGJ?= <foo@example.com>')
    run_full_mailbox_test(u'foo❕ <foo@example.com>',
        EmailAddress(u'foo❕', u'foo@example.com'),
        '=?utf-8?b?Zm9v4p2V?= <foo@example.com>')
    run_full_mailbox_test(u'foo❗ <foo@example.com>',
        EmailAddress(u'foo❗', u'foo@example.com'),
        '=?utf-8?b?Zm9v4p2X?= <foo@example.com>')
    run_full_mailbox_test(u'foo❢ <foo@example.com>',
        EmailAddress(u'foo❢', u'foo@example.com'),
        '=?utf-8?b?Zm9v4p2i?= <foo@example.com>')
    run_full_mailbox_test(u'foo❣ <foo@example.com>',
        EmailAddress(u'foo❣', u'foo@example.com'),
        '=?utf-8?b?Zm9v4p2j?= <foo@example.com>')
    run_full_mailbox_test(u'fooꜝ <foo@example.com>',
        EmailAddress(u'fooꜝ', u'foo@example.com'),
        '=?utf-8?b?Zm9v6pyd?= <foo@example.com>')
    run_full_mailbox_test(u'fooꜞ <foo@example.com>',
        EmailAddress(u'fooꜞ', u'foo@example.com'),
        '=?utf-8?b?Zm9v6pye?= <foo@example.com>')
    run_full_mailbox_test(u'fooꜟ <foo@example.com>',
        EmailAddress(u'fooꜟ', u'foo@example.com'),
        '=?utf-8?b?Zm9v6pyf?= <foo@example.com>')
    run_full_mailbox_test(u'foo﹗ <foo@example.com>',
        EmailAddress(u'foo﹗', u'foo@example.com'),
        '=?utf-8?b?Zm9v77mX?= <foo@example.com>')
    run_full_mailbox_test(u'foo！ <foo@example.com>',
        EmailAddress(u'foo！', u'foo@example.com'),
        '=?utf-8?b?Zm9v77yB?= <foo@example.com>')
    run_full_mailbox_test(u'foo՜ <foo@example.com>',
        EmailAddress(u'foo՜', u'foo@example.com'),
        '=?utf-8?b?Zm9v1Zw=?= <foo@example.com>')
    run_full_mailbox_test(u'foo߹ <foo@example.com>',
        EmailAddress(u'foo߹', u'foo@example.com'),
        '=?utf-8?b?Zm9v37k=?= <foo@example.com>')
    run_full_mailbox_test(u'foo႟ <foo@example.com>',
        EmailAddress(u'foo႟', u'foo@example.com'),
        '=?utf-8?b?Zm9v4YKf?= <foo@example.com>')
    run_full_mailbox_test(u'foo᥄ <foo@example.com>',
        EmailAddress(u'foo᥄', u'foo@example.com'),
        '=?utf-8?b?Zm9v4aWE?= <foo@example.com>')


def test_angle_addr():
    "Grammar: angle-addr -> [ whitespace ] < addr-spec > [ whitespace ]"

    # pass angle-addr
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
    run_mailbox_test(''.join(['a'*1025, '@b']), None)

    # because qtext and quoted-pair are longer than 64 bytes (limit on local-part)
    # we use a sample in testing, every other for qtext and every fifth for quoted-pair
    sample_qtext = FULL_QTEXT[::2]
    sample_qpair = FULL_QUOTED_PAIR[::5]
    sample_qpair_without_slashes = sample_qpair[1::2]

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
    run_mailbox_test(', steve@apple.com', None)
    run_mailbox_test(';;steve@apple.com', None)
    run_mailbox_test('"steve@apple.com', None)
    run_mailbox_test('steve"@apple.com', None)
    run_mailbox_test('steve..jobs@apple.com', None)

    # pass qtext
    for cnk in chunks(FULL_QTEXT, len(FULL_QTEXT)/2):
        run_mailbox_test('"{0}"@b'.format(cnk), '"{0}"@b'.format(cnk))
    run_mailbox_test('" {0}"@b'.format(sample_qtext), '" {0}"@b'.format(sample_qtext))
    run_mailbox_test('"{0} "@b'.format(sample_qtext), '"{0} "@b'.format(sample_qtext))
    run_mailbox_test('" {0} "@b'.format(sample_qtext), '" {0} "@b'.format(sample_qtext))
    run_full_mailbox_test('"{0}" <"{0}"@b>'.format(sample_qtext),
        EmailAddress(sample_qtext, '"{0}"@b'.format(sample_qtext)))

    # fail qtext
    run_mailbox_test('"{0}@b'.format(sample_qtext), None)
    run_mailbox_test('{0}"@b'.format(sample_qtext), None)
    run_mailbox_test('{0}@b'.format(sample_qtext), None)
    run_mailbox_test('"{0}@b"'.format(sample_qtext), None)

    # pass quoted-pair
    for cnk in chunks(FULL_QUOTED_PAIR, len(FULL_QUOTED_PAIR)/3):
        run_mailbox_test('"{0}"@b'.format(cnk), '"{0}"@b'.format(cnk))
    run_mailbox_test('" {0}"@b'.format(sample_qpair), '" {0}"@b'.format(sample_qpair))
    run_mailbox_test('"{0} "@b'.format(sample_qpair), '"{0} "@b'.format(sample_qpair))
    run_mailbox_test('" {0} "@b'.format(sample_qpair), '" {0} "@b'.format(sample_qpair))
    run_full_mailbox_test('"{0}" <"{0}"@b>'.format(sample_qpair),
        EmailAddress(sample_qpair_without_slashes, '"{0}"@b'.format(sample_qpair)))

    # fail quoted-pair
    run_mailbox_test('"{0}@b'.format(sample_qpair), None)
    run_mailbox_test('{0}"@b'.format(sample_qpair), None)
    run_mailbox_test('{0}@b'.format(sample_qpair), None)
    run_mailbox_test('"{0}@b"'.format(sample_qpair), None)


def test_domain():
    "Grammar: domain -> dot-atom"

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


def test_full_spec_symmetry_bug():
    """
    There was a bug that if an address has a display name that is equal or
    longer then 78 characters and consists of at least two words, then
    `full_spec` returned a string where a '\n' character was inserted between
    the display name words.
    """
    # Given
    original = 'very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong <foo@example.com>'
    addr = address.parse(original)

    # When
    restored = addr.full_spec()

    # Then
    assert_equal(original, restored)

