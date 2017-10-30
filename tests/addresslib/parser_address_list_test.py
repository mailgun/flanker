# coding:utf-8

from itertools import chain, combinations, permutations

from nose.tools import assert_equal, assert_not_equal, assert_raises, eq_
from nose.tools import nottest

from flanker.addresslib.address import EmailAddress, AddressList, parse_list, \
    parse


@nottest
def powerset(iterable):
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


@nottest
def run_test(string, expected_mlist):
    mlist = parse_list(string, strict=True)
    assert_equal(mlist, expected_mlist)


BILL_AS = EmailAddress(None, 'bill@microsoft.com')
STEVE_AS = EmailAddress(None, 'steve@apple.com')
LINUS_AS = EmailAddress(None, 'torvalds@kernel.org')

BILL_MBX = EmailAddress('Bill Gates', 'bill@microsoft.com')
STEVE_MBX = EmailAddress('Steve Jobs', 'steve@apple.com')
LINUS_MBX = EmailAddress('Linus Torvalds', 'torvalds@kernel.org')


def test_parse_list_from_list():
    for i, tc in enumerate([{
        'desc': 'Empty',
        'in': [],
        'good': AddressList(),
        'bad': []
    }, {
        'desc': 'All good',
        'in': [u'Bill Gates <bill@microsoft.com>',
               u'Федот <стрелец@почта.рф>',
               u'torvalds@kernel.org'],
        'good': AddressList([
            parse('Bill Gates <bill@microsoft.com>'),
            parse(u'Федот <стрелец@почта.рф>'),
            parse('torvalds@kernel.org')]),
        'bad': []
    }, {
        'desc': 'All bad',
        'in': ['httd://foo.com:8080\r\n',
               '"Ev K." <ev@ host.com>\n "Alex K" alex@',
               '"Tom, S" "tom+["  a]"@s.com'],
        'good': AddressList(),
        'bad': ['httd://foo.com:8080\r\n',
                '"Ev K." <ev@ host.com>\n "Alex K" alex@',
                '"Tom, S" "tom+["  a]"@s.com'],
        'bad_s': ['httd://foo.com:8080\r\n, "Ev K." <ev@ host.com>\n "Alex K" alex@, "Tom, S" "tom+["  a]"@s.com']
    }, {
        'desc': 'Some bad',
        'in': [u'Bill Gates <bill@microsoft.com>',
               u'crap',
               'foo.bar.com',
               u'Федот <стрелец@почта.рф>',
               'torvalds@@kernel.org'],
        'good': AddressList([
            parse('Bill Gates <bill@microsoft.com>'),
            parse(u'Федот <стрелец@почта.рф>')]),
        'good_s': AddressList(),
        'bad': ['crap',
                'foo.bar.com',
                'torvalds@@kernel.org'],
        'bad_s': [u'Bill Gates <bill@microsoft.com>, crap, foo.bar.com, Федот <стрелец@почта.рф>, torvalds@@kernel.org'],
    }, {
        'desc': 'Bad IDN among addresses (UTF-8)',
        'in': [u'Bill Gates <bill@microsoft.com>',
               u'foo@ドメイン.채ᅳ',
               u'Федот <стрелец@почта.рф>'],
        'good': AddressList([
            parse('Bill Gates <bill@microsoft.com>'),
            parse(u'Федот <стрелец@почта.рф>')]),
        'bad': [u'foo@ドメイン.채ᅳ']
    }, {
        'desc': 'Bad IDN among addresses (punycode)',
        'in': [u'Bill Gates <bill@microsoft.com>',
               u'foo@bar.xn--com-to0a',
               u'Федот <стрелец@почта.рф>'],
        'good': AddressList([
            parse('Bill Gates <bill@microsoft.com>'),
            parse(u'Федот <стрелец@почта.рф>')]),
        'bad': ['foo@bar.xn--com-to0a']
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))

        # When
        al = parse_list(tc['in'])
        al_from_l, bad_from_l = parse_list(tc['in'], as_tuple=True)
        al_from_s, bad_from_s = parse_list(', '.join(tc['in']), as_tuple=True)

        # Then
        eq_(tc['good'], al)
        eq_(tc['good'], al_from_l)
        for j in range(len(al_from_l)):
            _strict_eq(tc['good'][j], al[j])
            _strict_eq(tc['good'][j], al_from_l[j])
        eq_(tc['bad'], bad_from_l)

        eq_(tc.get('good_s', tc['good']), al_from_s)
        for j in range(len(al_from_s)):
            _strict_eq(tc.get('good_s', tc['good'])[j], al_from_s[j])
        eq_(tc.get('bad_s', tc['bad']), bad_from_s)


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


def test_append_address_only():
    # Only Address types can be added to an AddressList.

    al = AddressList()
    al.append(parse(u'Федот <стрелец@почта.рф>'))
    al.append(parse('https://mailgun.net/webhooks'))

    with assert_raises(TypeError):
        al.append('foo@bar.com')


def _strict_eq(lhs_addr, rhs_addr):
    eq_(type(lhs_addr), type(rhs_addr))
    _typed_eq(lhs_addr.address, rhs_addr.address)
    if isinstance(lhs_addr, EmailAddress):
        _typed_eq(lhs_addr.display_name, rhs_addr.display_name)


def _typed_eq(lhs, rhs):
    eq_(lhs, rhs)
    eq_(type(lhs), type(rhs))
