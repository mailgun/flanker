# coding:utf-8

from itertools import chain, combinations, permutations

from nose.tools import assert_equal, assert_not_equal
from nose.tools import nottest

from flanker.addresslib.address import EmailAddress, AddressList, parse_list


@nottest
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

@nottest
def run_test(string, expected_mlist):
    mlist = parse_list(string)
    assert_equal(mlist, expected_mlist)


BILL_AS = EmailAddress(None, 'bill@microsoft.com')
STEVE_AS = EmailAddress(None, 'steve@apple.com')
LINUS_AS = EmailAddress(None, 'torvalds@kernel.org')

BILL_MBX = EmailAddress('Bill Gates', 'bill@microsoft.com')
STEVE_MBX = EmailAddress('Steve Jobs', 'steve@apple.com')
LINUS_MBX = EmailAddress('Linus Torvalds', 'torvalds@kernel.org')


def test_sanity():
    addr_string = 'Bill Gates <bill@microsoft.com>, Steve Jobs <steve@apple.com>; torvalds@kernel.org'
    run_test(addr_string,  [BILL_MBX, STEVE_MBX, LINUS_AS])


def test_simple_valid():
    s = '''http://foo.com:8080; "Ev K." <ev@host.com>, "Alex K" <alex@yahoo.net>, "Tom, S" <"tom+[a]"@s.com>'''
    addrs = parse_list(s)

    assert_equal(4, len(addrs))

    assert_equal(addrs[0].addr_type, 'url')
    assert_equal(addrs[0].address, 'http://foo.com:8080')
    assert_equal(addrs[0].full_spec(), 'http://foo.com:8080')

    assert_equal(addrs[1].addr_type, 'email')
    assert_equal(addrs[1].display_name, 'Ev K.')
    assert_equal(addrs[1].address, 'ev@host.com')
    assert_equal(addrs[1].full_spec(), '"Ev K." <ev@host.com>')

    assert_equal(addrs[2].addr_type, 'email')
    assert_equal(addrs[2].display_name, 'Alex K')
    assert_equal(addrs[2].address, 'alex@yahoo.net')
    assert_equal(addrs[2].full_spec(), 'Alex K <alex@yahoo.net>')

    assert_equal(addrs[3].addr_type, 'email')
    assert_equal(addrs[3].display_name, 'Tom, S')
    assert_equal(addrs[3].address, '"tom+[a]"@s.com')
    assert_equal(addrs[3].full_spec(), '"Tom, S" <"tom+[a]"@s.com>')


    s = '''"Allan G\'o"  <allan@example.com>, "Os Wi" <oswi@example.com>'''
    addrs = parse_list(s)

    assert_equal(2, len(addrs))

    assert_equal(addrs[0].addr_type, 'email')
    assert_equal(addrs[0].display_name, 'Allan G\'o')
    assert_equal(addrs[0].address, 'allan@example.com')
    assert_equal(addrs[0].full_spec(), 'Allan G\'o <allan@example.com>')

    assert_equal(addrs[1].addr_type, 'email')
    assert_equal(addrs[1].display_name, 'Os Wi')
    assert_equal(addrs[1].address, 'oswi@example.com')
    assert_equal(addrs[1].full_spec(), 'Os Wi <oswi@example.com>')


    s = u'''I am also A <a@HOST.com>, Zeka <EV@host.coM> ;Gonzalo Bañuelos<gonz@host.com>'''
    addrs = parse_list(s)

    assert_equal(3, len(addrs))

    assert_equal(addrs[0].addr_type, 'email')
    assert_equal(addrs[0].display_name, 'I am also A')
    assert_equal(addrs[0].address, 'a@host.com')
    assert_equal(addrs[0].full_spec(), 'I am also A <a@host.com>')

    assert_equal(addrs[1].addr_type, 'email')
    assert_equal(addrs[1].display_name, 'Zeka')
    assert_equal(addrs[1].address, 'EV@host.com')
    assert_equal(addrs[1].full_spec(), 'Zeka <EV@host.com>')

    assert_equal(addrs[2].addr_type, 'email')
    assert_equal(addrs[2].display_name, u'Gonzalo Bañuelos')
    assert_equal(addrs[2].address, 'gonz@host.com')
    assert_equal(addrs[2].full_spec(), '=?utf-8?q?Gonzalo_Ba=C3=B1uelos?= <gonz@host.com>')


    s = r'''"Escaped" <"\e\s\c\a\p\e\d"@sld.com>; http://userid:password@example.com:8080, "Dmitry" <my|'`!#_~%$&{}?^+-*@host.com>'''
    addrs = parse_list(s)

    assert_equal(3, len(addrs))

    assert_equal(addrs[0].addr_type, 'email')
    assert_equal(addrs[0].display_name, 'Escaped')
    assert_equal(addrs[0].address, '"\e\s\c\\a\p\e\d"@sld.com')
    assert_equal(addrs[0].full_spec(), 'Escaped <"\e\s\c\\a\p\e\d"@sld.com>')

    assert_equal(addrs[1].addr_type, 'url')
    assert_equal(addrs[1].address, 'http://userid:password@example.com:8080')
    assert_equal(addrs[1].full_spec(), 'http://userid:password@example.com:8080')

    assert_equal(addrs[2].addr_type, 'email')
    assert_equal(addrs[2].display_name, 'Dmitry')
    assert_equal(addrs[2].address, 'my|\'`!#_~%$&{}?^+-*@host.com')
    assert_equal(addrs[2].full_spec(), 'Dmitry <my|\'`!#_~%$&{}?^+-*@host.com>')


    s = "http://foo.com/blah_blah_(wikipedia)"
    addrs = parse_list(s)

    assert_equal(1, len(addrs))

    assert_equal(addrs[0].addr_type, 'url')
    assert_equal(addrs[0].address, 'http://foo.com/blah_blah_(wikipedia)')
    assert_equal(addrs[0].full_spec(), 'http://foo.com/blah_blah_(wikipedia)')


    s = "Sasha Klizhentas <klizhentas@gmail.com>"
    addrs = parse_list(s)

    assert_equal(1, len(addrs))

    assert_equal(addrs[0].addr_type, 'email')
    assert_equal(addrs[0].display_name, 'Sasha Klizhentas')
    assert_equal(addrs[0].address, 'klizhentas@gmail.com')
    assert_equal(addrs[0].full_spec(), 'Sasha Klizhentas <klizhentas@gmail.com>')


    s = "admin@mailgunhq.com,lift@example.com"
    addrs = parse_list(s)

    assert_equal(2, len(addrs))

    assert_equal(addrs[0].addr_type, 'email')
    assert_equal(addrs[0].display_name, '')
    assert_equal(addrs[0].address, 'admin@mailgunhq.com')
    assert_equal(addrs[0].full_spec(), 'admin@mailgunhq.com')

    assert_equal(addrs[1].addr_type, 'email')
    assert_equal(addrs[1].display_name, '')
    assert_equal(addrs[1].address, 'lift@example.com')
    assert_equal(addrs[1].full_spec(), 'lift@example.com')


def test_simple_invalid():
    s = '''httd://foo.com:8080\r\n; "Ev K." <ev@ host.com>\n "Alex K" alex@ , "Tom, S" "tom+["  a]"@s.com'''
    assert_equal(AddressList(), parse_list(s))

    s = ""
    assert_equal(AddressList(), parse_list(s))

    s = "crap"
    assert_equal(AddressList(), parse_list(s))


def test_endpoints():
    # expected result: [foo@example.com, baz@example.com]
    presult = parse_list('foo@example.com, bar, baz@example.com', as_tuple=False)
    assert isinstance(presult, AddressList)
    assert_equal(0, len(presult))

    # expected result: ([foo@example.com, baz@example.com], ['bar'])
    presult = parse_list(['foo@example.com', 'bar', 'baz@example.com'], as_tuple=True)
    assert type(presult) is tuple
    assert_equal(2, len(presult[0]))
    assert_equal(1, len(presult[1]))


def test_delimiters():
    # permutations
    for e in permutations('  ,,;;'):
        addr_string = 'bill@microsoft.com' + ''.join(e) + 'steve@apple.com, torvalds@kernel.org'
        run_test(addr_string, [BILL_AS, STEVE_AS, LINUS_AS])

    # powerset
    for e in powerset('  ,,;;'):
        # empty sets will be tested by the synchronize tests
        if ''.join(e).strip() == '':
            continue

        addr_string = 'bill@microsoft.com' + ''.join(e) + 'steve@apple.com, torvalds@kernel.org'
        run_test(addr_string, [BILL_AS, STEVE_AS, LINUS_AS])
