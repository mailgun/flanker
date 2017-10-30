# coding:utf-8
import six
from nose.tools import assert_raises, eq_, ok_

from flanker.addresslib.address import (Address, AddressList, EmailAddress,
                                        UrlAddress)
from flanker.addresslib.address import parse, parse_list


def test_addr_properties():
    email = parse('name@host.com')
    url = parse('http://host.com')
    non_ascii = parse(u'Gonzalo Bañuelos<gonz@host.com>')

    eq_(False, url.supports_routing)
    eq_(True,  email.supports_routing)

    eq_(Address.Type.Email, email.addr_type)
    eq_(Address.Type.Url, url.addr_type)
    eq_(non_ascii, "gonz@host.com")

    adr = parse("Zeka <EV@host.coM>")
    eq_(str(adr), 'EV@host.com')


def test_address_compare():
    a = EmailAddress("a@host.com")
    b = EmailAddress("b@host.com")
    also_a = EmailAddress("A@host.com")

    ok_(a == also_a)
    #eq_(False, a != "I am also A <a@HOST.com>")
    ok_(a != 'crap')
    ok_(a != None)
    ok_(a != b)

    u = UrlAddress("http://hello.com")
    ok_(u == "http://hello.com")

    # make sure it works for sets:
    s = set()
    s.add(a)
    s.add(also_a)
    eq_(1, len(s))
    s.add(u)
    s.add(u)
    eq_(2, len(s))

    # test string comparison
    ok_(a == a.address)
    ok_(not (a != a.address))

    ok_(b != a.address)
    ok_(not (b == a.address))


def test_local_url():
    u = UrlAddress('http:///foo/bar')
    eq_(None, u.hostname)


def test_addresslist_basics():
    lst = parse_list("http://foo.com:1000; Biz@Kontsevoy.Com   ")
    eq_(2, len(lst))
    eq_("http", lst[0].scheme)
    eq_("kontsevoy.com", lst[1].hostname)
    eq_("Biz", lst[1].mailbox)
    ok_("biz@kontsevoy.com" in lst)

    # test case-sensitivity: hostname must be lowercased, but the local-part needs
    # to remain case-sensitive
    ok_("Biz@kontsevoy.com" in str(lst))

    # check parsing:
    spec = '''http://foo.com:8080, "Ev K." <ev@host.com>, "Alex K" <alex@yahoo.net>; "Tom, S" <"tom+[a]"@s.com>'''
    lst = parse_list(spec, True)

    eq_(len(lst), 4)
    eq_("http://foo.com:8080", lst[0].address)
    eq_("ev@host.com", lst[1].address)
    eq_("alex@yahoo.net", lst[2].address)
    eq_('"tom+[a]"@s.com', lst[3].address)

    # string-based persistence:
    s = str(lst)
    clone = parse_list(s)
    eq_(lst, clone)

    # now clone using full spec:
    s = lst.full_spec()
    clone = parse_list(s)
    eq_(lst, clone)

    # hostnames:
    eq_({'host.com', 'foo.com', 'yahoo.net', 's.com'}, lst.hostnames)
    eq_({'url', 'email'}, lst.addr_types)

    # add:
    result = lst + parse_list("ev@local.net") + ["foo@bar.com"]
    ok_(isinstance(result, AddressList))
    eq_(len(result), len(lst)+2)
    ok_("foo@bar.com" in result)


def test_addresslist_with_apostrophe():
    s = '''"Allan G\'o"  <allan@example.com>, "Os Wi" <oswi@example.com>'''
    lst = parse_list(s)
    eq_(2, len(lst))
    eq_('Allan G\'o <allan@example.com>', lst[0].full_spec())
    eq_('Os Wi <oswi@example.com>', lst[1].full_spec())
    lst = parse_list("Eugueny ώ Kontsevoy <eugueny@gmail.com>")
    eq_('=?utf-8?q?Eugueny_=CF=8E_Kontsevoy?= <eugueny@gmail.com>', lst.full_spec())
    eq_(u'Eugueny ώ Kontsevoy', lst[0].display_name)


def test_addresslist_non_ascii_list_input():
    al = [u'Aurélien Berger  <ab@example.com>', 'Os Wi <oswi@example.com>']
    lst = parse_list(al)
    eq_(2, len(lst))
    eq_('=?utf-8?q?Aur=C3=A9lien_Berger?= <ab@example.com>', lst[0].full_spec())
    eq_('Os Wi <oswi@example.com>', lst[1].full_spec())


def test_addresslist_address_obj_list_input():
    al = [EmailAddress(u'Aurélien Berger  <ab@example.com>'),
          UrlAddress('https://www.example.com')]
    lst = parse_list(al)
    eq_(2, len(lst))
    eq_('=?utf-8?q?Aur=C3=A9lien_Berger?= <ab@example.com>',
        lst[0].full_spec())
    eq_('https://www.example.com', lst[1].full_spec())


def test_edge_cases():
    email = EmailAddress('"foo.bar@"@example.com')
    eq_('"foo.bar@"@example.com', email.address)


def test_display_name__to_full_spec():
    eq_('"foo (\\"bar\\") blah" <foo@bar.com>',
        EmailAddress('foo ("bar") blah', 'foo@bar.com').full_spec())
    eq_('foo. bar <foo@bar.com>',
        EmailAddress('foo. bar', 'foo@bar.com').full_spec())
    eq_('"\\"\\"" <foo@bar.com>',
        EmailAddress('""', 'foo@bar.com').full_spec()),
    eq_('=?utf-8?b?0J/RgNC40LLQtdGCINCc0LXQtNCy0LXQtA==?= <foo@bar.com>',
        EmailAddress(u'Привет Медвед', 'foo@bar.com').full_spec())


def test_address_convertible_2_ascii():
    for i, tc in enumerate([{
        'desc': 'display_name=empty, domain=ascii',
        'addr': 'Foo@Bar.com',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Foo@bar.com',
        'str':               'Foo@bar.com',
        'unicode':          u'Foo@bar.com',
        'full_spec':         'Foo@bar.com',
    }, {
        'desc': 'display_name=ascii, domain=ascii',
        'addr': 'Blah <Foo@Bar.com>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Blah <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'Blah <Foo@bar.com>',
        'full_spec':         'Blah <Foo@bar.com>',
    }, {
        'desc': 'display_name=utf8, domain=ascii',
        'addr': u'Федот <Foo@Bar.com>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Федот <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'Федот <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=ascii',
        'addr': '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@Bar.com>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Федот <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'Федот <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=bad-encoding, domain=ascii',
        'addr': '=?blah0KTQtdC00L7Rgg==?= <Foo@Bar.com>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Foo@bar.com>',
        'full_spec':         '=?blah0KTQtdC00L7Rgg==?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=empty, domain=utf8',
        'addr': u'Foo@Почта.рф',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Foo@почта.рф',
        'str':               'Foo@почта.рф',
        'unicode':          u'Foo@почта.рф',
        'full_spec':         'Foo@xn--80a1acny.xn--p1ai',
    }, {
        'desc': 'display_name=ascii, domain=utf8',
        'addr': u'Blah <Foo@Почта.рф>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Blah <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Blah <Foo@почта.рф>',
        'full_spec':         'Blah <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=utf8, domain=utf8',
        'addr': u'Федот <Foo@Почта.рф>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Федот <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Федот <Foo@почта.рф>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=utf8',
        'addr': u'=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@Почта.рф>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Федот <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Федот <Foo@почта.рф>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=bad-encoding, domain=utf8',
        'addr': u'=?blah0KTQtdC00L7Rgg==?= <Foo@Почта.рф>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Foo@почта.рф>',
        'full_spec':         '=?blah0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=empty, domain=punycode',
        'addr': 'Foo@xn--80a1acny.xn--p1ai',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Foo@почта.рф',
        'str':               'Foo@почта.рф',
        'unicode':          u'Foo@почта.рф',
        'full_spec':         'Foo@xn--80a1acny.xn--p1ai',
    }, {
        'desc': 'display_name=ascii, domain=punycode',
        'addr': 'Blah <Foo@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Blah <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Blah <Foo@почта.рф>',
        'full_spec':         'Blah <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=utf8, domain=punycode',
        'addr': 'Федот <Foo@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Федот <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Федот <Foo@почта.рф>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=punycode',
        'addr': '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              'Федот <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'Федот <Foo@почта.рф>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=bad-encoding, domain=punycode',
        'addr': '=?blah0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Foo@почта.рф',
        'ace_address':       'Foo@xn--80a1acny.xn--p1ai',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Foo@почта.рф>',
        'str':               'Foo@почта.рф',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Foo@почта.рф>',
        'full_spec':         '=?blah0KTQtdC00L7Rgg==?= <Foo@xn--80a1acny.xn--p1ai>',
    }, {
        'desc': 'display_name=utf8, domain=partial-punycode',
        'addr': u'Федот <Foo@mail.xn--com-9ma>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'mail.comñ',
        'ace_hostname':      'mail.xn--com-9ma',
        'address':          u'Foo@mail.comñ',
        'ace_address':       'Foo@mail.xn--com-9ma',
        'repr':              'Федот <Foo@mail.comñ>',
        'str':               'Foo@mail.comñ',
        'unicode':          u'Федот <Foo@mail.comñ>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7Rgg==?= <Foo@mail.xn--com-9ma>',
    }, {
        'desc': 'display_name=quoted-utf8-with-period, domain=ascii',
        'addr': u'"Федот . Стрелец" <Foo@Bar.com>',

        'display_name':     u'Федот . Стрелец',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7RgiAuINCh0YLRgNC10LvQtdGG?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Федот . Стрелец <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'Федот . Стрелец <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7RgiAuINCh0YLRgNC10LvQtdGG?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=quoted-utf8-with-special, domain=ascii',
        'addr': u'"Федот @ Стрелец" <Foo@Bar.com>',

        'display_name':     u'Федот @ Стрелец',
        'ace_display_name':  '=?utf-8?b?ItCk0LXQtNC+0YIgQCDQodGC0YDQtdC70LXRhiI=?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              '"Федот @ Стрелец" <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'"Федот @ Стрелец" <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?ItCk0LXQtNC+0YIgQCDQodGC0YDQtdC70LXRhiI=?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=quoted-and-encoded-utf8-with-period, domain=ascii',
        'addr': u'=?utf-8?b?ItCk0LXQtNC+0YIgLiDQodGC0YDQtdC70LXRhiI=?= <Foo@Bar.com>',

        'display_name':     u'Федот . Стрелец',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7RgiAuINCh0YLRgNC10LvQtdGG?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              'Федот . Стрелец <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'Федот . Стрелец <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?0KTQtdC00L7RgiAuINCh0YLRgNC10LvQtdGG?= <Foo@bar.com>',
    }, {
        'desc': 'display_name=quoted-and-encoded-utf8-with-special, domain=ascii',
        'addr': u'=?utf-8?b?ItCk0LXQtNC+0YIgQCDQodGC0YDQtdC70LXRhiI=?= <Foo@Bar.com>',

        'display_name':     u'Федот @ Стрелец',
        'ace_display_name':  '=?utf-8?b?ItCk0LXQtNC+0YIgQCDQodGC0YDQtdC70LXRhiI=?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Foo@bar.com',
        'ace_address':       'Foo@bar.com',
        'repr':              '"Федот @ Стрелец" <Foo@bar.com>',
        'str':               'Foo@bar.com',
        'unicode':          u'"Федот @ Стрелец" <Foo@bar.com>',
        'full_spec':         '=?utf-8?b?ItCk0LXQtNC+0YIgQCDQodGC0YDQtdC70LXRhiI=?= <Foo@bar.com>',
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))
        # When
        addr = parse(tc['addr'])
        # Then
        assert isinstance(addr, EmailAddress)
        _typed_eq(False, addr.requires_non_ascii())
        _typed_eq(tc['display_name'], addr.display_name)
        _typed_eq(tc['ace_display_name'], addr.ace_display_name)
        _typed_eq(tc['hostname'], addr.hostname)
        _typed_eq(tc['ace_hostname'], addr.ace_hostname)
        _typed_eq(tc['address'], addr.address)
        _typed_eq(tc['ace_address'], addr.ace_address)
        _typed_eq(tc['repr'], repr(addr))
        _typed_eq(tc['str'], str(addr))
        if six.PY2:
            _typed_eq(tc['unicode'], unicode(addr))
        _typed_eq(tc['unicode'], addr.to_unicode())
        _typed_eq(tc['full_spec'], addr.full_spec())


def test_address_requires_utf8():
    for i, tc in enumerate([{
        'desc': 'display_name=empty, domain=ascii',
        'addr': u'Фью@Bar.com',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Фью@bar.com',
        'repr':              'Фью@bar.com',
        'str':               'Фью@bar.com',
        'unicode':          u'Фью@bar.com',
    }, {
        'desc': 'display_name=ascii, domain=ascii',
        'addr': u'Blah <Фью@Bar.com>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Фью@bar.com',
        'repr':              'Blah <Фью@bar.com>',
        'str':               'Фью@bar.com',
        'unicode':          u'Blah <Фью@bar.com>',
    }, {
        'desc': 'display_name=utf8, domain=ascii',
        'addr': u'Федот <Фью@Bar.com>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Фью@bar.com',
        'repr':              'Федот <Фью@bar.com>',
        'str':               'Фью@bar.com',
        'unicode':          u'Федот <Фью@bar.com>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=ascii',
        'addr': u'=?utf-8?b?0KTQtdC00L7Rgg==?= <Фью@Bar.com>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Фью@bar.com',
        'repr':              'Федот <Фью@bar.com>',
        'str':               'Фью@bar.com',
        'unicode':          u'Федот <Фью@bar.com>',
    }, {
        'desc': 'display_name=bad-encoding, domain=ascii',
        'addr': u'=?blah0KTQtdC00L7Rgg==?= <Фью@Bar.com>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'bar.com',
        'ace_hostname':      'bar.com',
        'address':          u'Фью@bar.com',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Фью@bar.com>',
        'str':               'Фью@bar.com',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Фью@bar.com>',
    }, {
        'desc': 'display_name=empty, domain=utf8',
        'addr': u'Фью@Почта.рф',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Фью@почта.рф',
        'str':               'Фью@почта.рф',
        'unicode':          u'Фью@почта.рф',
    }, {
        'desc': 'display_name=ascii, domain=utf8',
        'addr': u'Blah <Фью@Почта.рф>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Blah <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Blah <Фью@почта.рф>',
    }, {
        'desc': 'display_name=utf8, domain=utf8',
        'addr': u'Федот <Фью@Почта.рф>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Федот <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Федот <Фью@почта.рф>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=utf8',
        'addr': u'=?utf-8?b?0KTQtdC00L7Rgg==?= <Фью@Почта.рф>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Федот <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Федот <Фью@почта.рф>',
    }, {
        'desc': 'display_name=bad-encoding, domain=utf8',
        'addr': u'=?blah0KTQtdC00L7Rgg==?= <Фью@Почта.рф>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Фью@почта.рф>',
    }, {
        'desc': 'display_name=empty, domain=punycode',
        'addr': u'Фью@xn--80a1acny.xn--p1ai',

        'display_name':     u'',
        'ace_display_name':  '',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Фью@почта.рф',
        'str':               'Фью@почта.рф',
        'unicode':          u'Фью@почта.рф',
    }, {
        'desc': 'display_name=ascii, domain=punycode',
        'addr': u'Blah <Фью@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Blah',
        'ace_display_name':  'Blah',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Blah <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Blah <Фью@почта.рф>',
    }, {
        'desc': 'display_name=utf8, domain=punycode',
        'addr': u'Федот <Фью@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Федот <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Федот <Фью@почта.рф>',
    }, {
        'desc': 'display_name=encoded-utf8, domain=punycode',
        'addr': u'=?utf-8?b?0KTQtdC00L7Rgg==?= <Фью@xn--80a1acny.xn--p1ai>',

        'display_name':     u'Федот',
        'ace_display_name':  '=?utf-8?b?0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              'Федот <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'Федот <Фью@почта.рф>',
    }, {
        'desc': 'display_name=bad-encoding, domain=punycode',
        'addr': u'=?blah0KTQtdC00L7Rgg==?= <Фью@xn--80a1acny.xn--p1ai>',

        'display_name':     u'=?blah0KTQtdC00L7Rgg==?=',
        'ace_display_name':  '=?blah0KTQtdC00L7Rgg==?=',
        'hostname':         u'почта.рф',
        'ace_hostname':      'xn--80a1acny.xn--p1ai',
        'address':          u'Фью@почта.рф',
        'repr':              '=?blah0KTQtdC00L7Rgg==?= <Фью@почта.рф>',
        'str':               'Фью@почта.рф',
        'unicode':          u'=?blah0KTQtdC00L7Rgg==?= <Фью@почта.рф>',
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))
        # When
        addr = parse(tc['addr'])
        # Then
        assert isinstance(addr, EmailAddress)
        _typed_eq(True, addr.requires_non_ascii())
        _typed_eq(tc['display_name'], addr.display_name)
        _typed_eq(tc['ace_display_name'], addr.ace_display_name)
        _typed_eq(tc['hostname'], addr.hostname)
        _typed_eq(tc['ace_hostname'], addr.ace_hostname)
        _typed_eq(tc['address'], addr.address)
        with assert_raises(ValueError):
            _ = addr.ace_address
        _typed_eq(tc['repr'], repr(addr))
        _typed_eq(tc['str'], str(addr))
        if six.PY2:
            _typed_eq(tc['unicode'], unicode(addr))
        _typed_eq(tc['unicode'], addr.to_unicode())
        with assert_raises(ValueError):
            addr.full_spec()


def test_parse_bad_idna():
    # Some unicode addresses may seem ok at first sight, but in fact be invalid
    # because they contain not allowed unicode characters. Regardless whether
    # they are presented in punycode or UTF-8 form.

    for i, tc in enumerate([{
        'desc': 'Invalid IDNA domain (punycode)',
        'addr': 'foo@xn--eckwd4c7c.xn--8sd3676g',
    }, {
        'desc': 'Invalid IDNA domain (UTF-8)',
        'addr': 'foo@ドメイン.채ᅳ',
    }, {
        'desc': 'Invalid IDNA alabel',
        'addr': 'foo@bar.xn--com-to0a',
    }, {
        'desc': 'Invalid IDNA ulabel',
        'addr': 'foo@bar.com’',
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))
        # When/Then
        eq_(None, parse(tc['addr']))


def test_address_properties_req_utf8():
    for i, tc in enumerate([{
        'desc': 'utf8',
        'addr_list': u'"Федот" <стрелец@письмо.рф>, Марья <искусница@mail.gun>',

        'repr':       '[Федот <стрелец@письмо.рф>, Марья <искусница@mail.gun>]',
        'str':        'стрелец@письмо.рф, искусница@mail.gun',
        'unicode':   u'Федот <стрелец@письмо.рф>, Марья <искусница@mail.gun>',
        'full_spec':  ValueError(),
    }]):
        print('Test case #%d' % i)
        addr_list = parse_list(tc['addr_list'])
        eq_(tc['repr'], repr(addr_list))
        eq_(tc['str'], str(addr_list))
        if six.PY2:
            eq_(tc['unicode'], unicode(addr_list))
        eq_(tc['unicode'], addr_list.to_unicode())
        if isinstance(tc['full_spec'], Exception):
            assert_raises(type(tc['full_spec']), addr_list.full_spec)
        else:
            eq_(tc['full_spec'], addr_list.full_spec())


def test_address_full_spec_smart_quote_display_name():
    eq_(EmailAddress('foo',         'foo@bar.com').full_spec(), 'foo <foo@bar.com>')
    eq_(EmailAddress('()<>[]:;@,.', 'foo@bar.com').full_spec(), '"()<>[]:;@,." <foo@bar.com>')
    eq_(EmailAddress('"',           'foo@bar.com').full_spec(), '"\\"" <foo@bar.com>')
    eq_(EmailAddress('\\',          'foo@bar.com').full_spec(), '"\\\\" <foo@bar.com>')


def test_address_unicode_smart_quote_display_name():
    eq_(EmailAddress('foo',         'foo@bar.com').to_unicode(), u'foo <foo@bar.com>')
    eq_(EmailAddress('()<>[]:;@,.', 'foo@bar.com').to_unicode(), u'"()<>[]:;@,." <foo@bar.com>')
    eq_(EmailAddress('"',           'foo@bar.com').to_unicode(), u'"\\"" <foo@bar.com>')
    eq_(EmailAddress('\\',          'foo@bar.com').to_unicode(), u'"\\\\" <foo@bar.com>')
    eq_(EmailAddress('Федот',       'foo@bar.com').to_unicode(), u'Федот <foo@bar.com>')
    eq_(EmailAddress('<Федот>',     'foo@bar.com').to_unicode(), u'"<Федот>" <foo@bar.com>')


def test_contains_non_ascii():
    eq_(EmailAddress(None, 'foo@bar.com').contains_non_ascii(), False)
    eq_(EmailAddress(None, 'foo@экзампл.рус').contains_non_ascii(), True)
    eq_(EmailAddress(None, 'аджай@bar.com').contains_non_ascii(), True)
    eq_(EmailAddress(None, 'аджай@экзампл.рус').contains_non_ascii(), True)


def test_contains_domain_literal():
    eq_(EmailAddress(None, 'foo@bar.com').contains_domain_literal(), False)
    eq_(EmailAddress(None, 'foo@[1.2.3.4]').contains_domain_literal(), True)


def test_parse_relaxed():
    eq_(u'foo <foo@bar.com>',             parse('foo <foo@bar.com>').to_unicode())
    eq_(u'foo <foo@bar.com>',             parse('foo foo@bar.com').to_unicode())
    eq_(u'foo <foo@bar.com>',             parse('foo (comment) <foo@bar.com>').to_unicode())
    eq_(u'"foo (comment)" <foo@bar.com>', parse('foo (comment) foo@bar.com').to_unicode())
    eq_(u'"not@valid" <foo@bar.com>',     parse('not@valid <foo@bar.com>').to_unicode())
    eq_(u'"not@valid" <foo@bar.com>',     parse('not@valid foo@bar.com').to_unicode())
    eq_(u'Маруся <мария@example.com>',    parse('Маруся мария@example.com').to_unicode())


def test_parse_list_relaxed():
    addr_list = ['foo <foo@bar.com>', 'foo foo@bar.com', 'not@valid <foo@bar.com>']
    expected = ['foo <foo@bar.com>', 'foo <foo@bar.com>', '"not@valid" <foo@bar.com>']
    eq_(expected, [addr.to_unicode() for addr in parse_list(addr_list)])


def _typed_eq(lhs, rhs):
    eq_(lhs, rhs)
    eq_(type(lhs), type(rhs))
