# coding=utf-8
from nose.tools import eq_
from flanker.addresslib.quote import smart_quote, smart_unquote


def test_quote():
    eq_('"foo, bar"', smart_quote('foo, bar'))
    eq_('"foo; bar"', smart_quote('foo; bar'))
    eq_('"foo< bar"', smart_quote('foo< bar'))
    eq_('"foo> bar"', smart_quote('foo> bar'))
    eq_('"foo\\" bar"', smart_quote('foo" bar'))
    eq_('"foo. bar"', smart_quote('foo. bar'))
    eq_('"foo: bar"', smart_quote('foo: bar'))


def test_quote__spaces():
    eq_('foo bar', smart_quote('foo bar'))
    eq_('" foo bar"', smart_quote(' foo bar'))
    eq_('"foo bar "', smart_quote('foo bar '))
    eq_('" foo bar "', smart_quote(' foo bar '))
    eq_('foo\tbar', smart_quote('foo\tbar'))
    eq_('"\tfoo\tbar"', smart_quote('\tfoo\tbar'))
    eq_('"foo\tbar\t"', smart_quote('foo\tbar\t'))
    eq_('"\tfoo\tbar\t"', smart_quote('\tfoo\tbar\t'))


def test_quote__escaping():
    eq_('"f\\\\o\\"o \\"bar\\""', smart_quote('f\\o"o "bar"'))
    eq_('"\\"foo\\""', smart_quote('"foo"'))
    eq_('"\\"foo\\"bar\\""', smart_quote('"foo"bar"'))


def test_quote__nothing_to_quote():
    eq_('', smart_quote(''))
    eq_('foo bar', smart_quote('foo bar'))
    eq_("!#$%&'*+-/=?^_`{|}~",
        smart_quote("!#$%&'*+-/=?^_`{|}~"))


def test_unquote():
    eq_('foo bar "(bazz)" blah oops',
        smart_unquote('foo "bar \\"(bazz)\\" blah" oops'))
    eq_('foo;  bar. \\bazz\\', smart_unquote('"foo;"  "bar." "\\\\bazz\\\\"'))
    eq_('"foo"bar"', smart_unquote('"\\"foo\\"bar\\"'))


def test_unquote__nothing_to_unquote():
    eq_('foo\\.;\tbar', smart_unquote('foo\\.;\tbar'))


def test_unquote__unicode():
    eq_(u'Превед Медвед', smart_unquote(u'Превед Медвед'))
