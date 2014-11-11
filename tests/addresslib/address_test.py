# coding:utf-8

from .. import *
from nose.tools import assert_equal, assert_not_equal

from flanker.addresslib.address import parse, parse_list
from flanker.addresslib.address import Address, AddressList, EmailAddress, UrlAddress


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


def test_gmail_dots():
    spec_only, full = True, False
    valid = (('example.@gmail.com', spec_only),
             ('...e.x.a.m.p.l.e...@gmail.com', spec_only),
             ('ex...ample@gmail.com', spec_only),
             ('example@gmail.com', spec_only),
             ('Example Jones <example.jones...@gmail.com>', full))
    invalid=(('.@gmail.com', spec_only),
             ('example@.gmail.com', spec_only),
             ('.........@gmail.com', spec_only),
             ('@gmail.com', spec_only),
             ('Example Jones <......@gmail.com>', full))

    for v, b in valid:
        eq_(v, parse(v, addr_spec_only=b))
    for v, b in invalid:
        eq_(None, parse(v, addr_spec_only=b))


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
    spec = '''http://foo.com:8080, "Ev K." <ev@host.com>, "Alex K" alex@yahoo.net; "Tom, S" "tom+[a]"@s.com'''
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
    eq_(set(['host.com', 'foo.com', 'yahoo.net', 's.com']), lst.hostnames)
    eq_(set(['url', 'email']), lst.addr_types)

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
    lst = parse_list("=?UTF-8?Q?Eugueny_=CF=8E_Kontsevoy?= <eugueny@gmail.com>")
    eq_('=?utf-8?q?Eugueny_=CF=8E_Kontsevoy?= <eugueny@gmail.com>', lst.full_spec())
    eq_(u'Eugueny ώ Kontsevoy', lst[0].display_name)


def test_edge_cases():
    email = EmailAddress('"foo.bar@"@example.com')
    eq_('"foo.bar@"@example.com', email.address)


def test_display_name__to_full_spec():
    eq_('"foo (\\"bar\\") blah" <foo@bar.com>',
        EmailAddress('foo ("bar") blah', 'foo@bar.com').full_spec())
    eq_('"foo. bar" <foo@bar.com>',
        EmailAddress('foo. bar', 'foo@bar.com').full_spec())
    eq_('"\\"\\"" <foo@bar.com>',
        EmailAddress('""', 'foo@bar.com').full_spec()),
    eq_('=?utf-8?b?0J/RgNC40LLQtdGCINCc0LXQtNCy0LXQtA==?= <foo@bar.com>',
        EmailAddress(u'Привет Медвед', 'foo@bar.com').full_spec())


def test_display_name__update():
    # Given
    a = EmailAddress('foo bar', 'foo@bar.com')
    eq_('foo bar <foo@bar.com>', a.full_spec())

    # When
    a.display_name = u'Привет Медвед'

    # Then
    eq_('=?utf-8?b?0J/RgNC40LLQtdGCINCc0LXQtNCy0LXQtA==?= <foo@bar.com>',
        a.full_spec())
