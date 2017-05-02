# coding:utf-8

from .. import *
from nose.tools import assert_equal, assert_not_equal, assert_raises

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
    eq_('"foo. bar" <foo@bar.com>',
        EmailAddress('foo. bar', 'foo@bar.com').full_spec())
    eq_('"\\"\\"" <foo@bar.com>',
        EmailAddress('""', 'foo@bar.com').full_spec()),
    eq_('=?utf-8?b?0J/RgNC40LLQtdGCINCc0LXQtNCy0LXQtA==?= <foo@bar.com>',
        EmailAddress(u'Привет Медвед', 'foo@bar.com').full_spec())


def test_views():
    for i, tc in enumerate([{
        # Pure ASCII
        'addr': parse('foo <foo@bar.com>'),
        'repr': 'foo <foo@bar.com>',
        'str': 'foo@bar.com',
        'unicode': u'foo <foo@bar.com>',
        'full_spec': 'foo <foo@bar.com>',
    }, {
        # UTF-8
        'addr': parse(u'Федот <стрелец@письмо.рф>'),
        'repr': 'Федот <стрелец@письмо.рф>',
        'str': 'стрелец@письмо.рф',
        'unicode': u'Федот <стрелец@письмо.рф>',
        'full_spec': ValueError(),
    }, {
        # UTF-8
        'addr': parse(u'"Федот" <стрелец@письмо.рф>'),
        'repr': 'Федот <стрелец@письмо.рф>',
        'str': 'стрелец@письмо.рф',
        'unicode': u'Федот <стрелец@письмо.рф>',
        'full_spec': ValueError(),
    }, {
        # ASCII with utf-8 encoded display name
        'addr': parse('=?utf-8?b?0LDQtNC20LDQuQ==?= <foo@bar.com>'),
        'repr': '=?utf-8?b?0LDQtNC20LDQuQ==?= <foo@bar.com>',
        'str': 'foo@bar.com',
        'unicode': '=?utf-8?b?0LDQtNC20LDQuQ==?= <foo@bar.com>',
        'full_spec': '=?utf-8?b?0LDQtNC20LDQuQ==?= <foo@bar.com>',
    }, {
        # IDNA domain
        'addr': parse('foo <foo@экзампл.рус>'),
        'repr': 'foo <foo@экзампл.рус>',
        'str': 'foo@экзампл.рус',
        'unicode': u'foo <foo@экзампл.рус>',
        'full_spec': 'foo <foo@xn--80aniges7g.xn--p1acf>',
    }, {
        # UTF-8 local part
        'addr': parse(u'foo <аджай@bar.com>'),
        'repr': 'foo <аджай@bar.com>',
        'str': 'аджай@bar.com',
        'unicode': u'foo <аджай@bar.com>',
        'full_spec': ValueError(),
    }, {
        # UTF-8 address list
        'addr': parse_list(u'"Федот" <стрелец@письмо.рф>, Марья <искусница@mail.gun>'),
        'repr': '[Федот <стрелец@письмо.рф>, Марья <искусница@mail.gun>]',
        'str': 'стрелец@письмо.рф, искусница@mail.gun',
        'unicode': u'Федот <стрелец@письмо.рф>, Марья <искусница@mail.gun>',
        'full_spec': ValueError(),
    }]):
        print('Test case #%d' % i)
        eq_(tc['repr'], repr(tc['addr']))
        eq_(tc['str'], str(tc['addr']))
        eq_(tc['unicode'], unicode(tc['addr']))
        eq_(tc['unicode'], tc['addr'].to_unicode())
        if isinstance(tc['full_spec'], Exception):
            assert_raises(type(tc['full_spec']), tc['addr'].full_spec)
        else:
            eq_(tc['full_spec'], tc['addr'].full_spec())


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


def test_requires_non_ascii():
    eq_(EmailAddress(None, 'foo@bar.com').requires_non_ascii(), False)
    eq_(EmailAddress(None, 'foo@экзампл.рус').requires_non_ascii(), False)
    eq_(EmailAddress(None, 'аджай@bar.com').requires_non_ascii(), True)
    eq_(EmailAddress(None, 'аджай@экзампл.рус').requires_non_ascii(), True)


def test_contains_domain_literal():
    eq_(EmailAddress(None, 'foo@bar.com').contains_domain_literal(), False)
    eq_(EmailAddress(None, 'foo@[1.2.3.4]').contains_domain_literal(), True)
