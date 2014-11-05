# coding:utf-8

from nose.tools import *
from mock import *
from flanker.mime.message.headers import encodedword
from flanker import utils
from flanker.mime.message import errors, charsets

def encoded_word_test():
    def t(value):
        m  = encodedword.encodedWord.match(value)
        return (m.group('charset'), m.group('encoding'), m.group('encoded'))

    r = t('=?utf-8?B?U2ltcGxlIHRleHQuIEhvdyBhcmUgeW91PyDQmtCw0Log0YLRiyDQv9C+0LY=?=')
    eq_(r[0], 'utf-8')
    eq_(r[1], 'B')
    eq_(r[2], 'U2ltcGxlIHRleHQuIEhvdyBhcmUgeW91PyDQmtCw0Log0YLRiyDQv9C+0LY=')

    r = t('=?UTF-8?Q?=D1=80=D1=83=D1=81=D1=81=D0=BA=D0=B8=D0=B9?=')
    eq_(r[0], 'UTF-8')
    eq_(r[1], 'Q')
    eq_(r[2], '=D1=80=D1=83=D1=81=D1=81=D0=BA=D0=B8=D0=B9')

    r = t('=?iso-8859-1?q?this=20is=20some=20text?=')
    eq_(r[0], 'iso-8859-1')
    eq_(r[1], 'q')
    eq_(r[2], 'this=20is=20some=20text')


def unfold_test():
    u = encodedword.unfold
    eq_('\t\t\t', u('\n\r\t\t\t'))
    eq_('\t\t\t', u('\n\t\t\t'))
    eq_('  ', u('\n\r  '))
    eq_('  ', u('\r\n  '))
    eq_('  ', u('\n  '))
    eq_('  ', u('\r  '))
    eq_(' \t', u('\n\r \t'))


def happy_mime_to_unicode_test():
    v = """   =?utf-8?B?U2ltcGxlIHRleHQuIEhvdyBhcmUgeW91PyDQmtCw0Log0YLRiyDQv9C+0LY=?=\n     =?utf-8?B?0LjQstCw0LXRiNGMPw==?="""
    eq_(u'Simple text. How are you? Как ты поживаешь?', encodedword.mime_to_unicode(v))

    v = ' =?US-ASCII?Q?Foo?= <foo@example.com>'
    eq_(u'Foo <foo@example.com>', encodedword.mime_to_unicode(v))

    v = '''=?UTF-8?Q?=D1=80=D1=83=D1=81=D1=81=D0=BA=D0=B8=D0=B9?=\n     =?UTF-8?Q?_=D0=B8?= english112      =?UTF-8?Q?=D1=81=D0=B0=D0=B1=D0=B6?= subject'''
    eq_(u'русский и english112      сабж subject', encodedword.mime_to_unicode(v))

    v = '=?iso-8859-1?B?SOlhdnkgTel05WwgVW7uY/hk?=\n\t=?iso-8859-1?Q?=E9?='
    eq_(u'Héavy Métål Unîcødé', encodedword.mime_to_unicode(v))


def lying_encodings_mime_to_unicode_test():
    v = '''=?US-ASCII?Q?=D1=80=D1=83=D1=81=D1=81=D0=BA=D0=B8=D0=B9?=\n  english112      =?UTF-8?Q?=D1=81=D0=B0=D0=B1=D0=B6?= subject'''
    eq_(u'русский  english112      сабж subject', encodedword.mime_to_unicode(v))


def missing_padding_mime_to_unicode_test():
    v = """   =?utf-8?B?U2ltcGxlIHRleHQuIEhvdyBhcmUgeW91PyDQmtCw0Log0YLRiyDQv9C+0LY?=\n     =?utf-8?B?0LjQstCw0LXRiNGMPw?="""
    eq_(u'Simple text. How are you? Как ты поживаешь?', encodedword.mime_to_unicode(v))


def neutral_headings_test():
    v = '''from mail-iy0-f179.google.com (mail-iy0-f179.google.com
\t[209.85.210.179])
\tby mxa.mailgun.org (Postfix) with ESMTP id 2D0D3F01116
\tfor <alex@mailgun.net>; Fri, 17 Dec 2010 12:50:07 +0000 (UTC)'''
    eq_(u'from mail-iy0-f179.google.com (mail-iy0-f179.google.com\t[209.85.210.179])\tby mxa.mailgun.org (Postfix) with ESMTP id 2D0D3F01116\tfor <alex@mailgun.net>; Fri, 17 Dec 2010 12:50:07 +0000 (UTC)', encodedword.mime_to_unicode(v))

    v = '''multipart/mixed; boundary="===============7553021138737466228=="'''
    eq_(v, encodedword.mime_to_unicode(v))


def outlook_encodings_test():
    v = '''=?koi8-r?B?/NTPINPPz8Ldxc7JxSDTIMTMyc7O2c0g08HC1sXL1M/NINPQxcPJwQ==?=
            =?koi8-r?B?zNjOzyDe1M/C2SDQ0s/XxdLJ1Nggy8/EydLP18vJ?='''
    eq_(u"Это сообщение с длинным сабжектом специально чтобы проверить кодировки", encodedword.mime_to_unicode(v))

def gmail_encodings_test():
    v = ''' =?KOI8-R?B?/NTPINPPz8Ldxc7JxSDTIMTMyc7O2c0g08HC1g==?=
            =?KOI8-R?B?xcvUz80g09DFw8nBzNjOzyDe1M/C2SDQ0s/XxdLJ1A==?=
                    =?KOI8-R?B?2CDLz8TJ0s/Xy8k=?='''
    eq_(u"Это сообщение с длинным сабжектом специально чтобы проверить кодировки", encodedword.mime_to_unicode(v))


def aol_encodings_test():
    v = ''' =?utf-8?Q?=D0=AD=D1=82=D0=BE_=D1=81=D0=BE=D0=BE=D0=B1=D1=89=D0=B5=D0=BD?=
     =?utf-8?Q?=D0=B8=D0=B5_=D1=81_=D0=B4=D0=BB=D0=B8=D0=BD=D0=BD=D1=8B=D0=BC?=
      =?utf-8?Q?_=D1=81=D0=B0=D0=B1=D0=B6=D0=B5=D0=BA=D1=82=D0=BE=D0=BC_=D1=81?=
       =?utf-8?Q?=D0=BF=D0=B5=D1=86=D0=B8=D0=B0=D0=BB=D1=8C=D0=BD=D0=BE_=D1=87?=
        =?utf-8?Q?=D1=82=D0=BE=D0=B1=D1=8B_=D0=BF=D1=80=D0=BE=D0=B2=D0=B5=D1=80?=
         =?utf-8?Q?=D0=B8=D1=82=D1=8C_=D0=BA=D0=BE=D0=B4=D0=B8=D1=80=D0=BE=D0=B2?=
          =?utf-8?Q?=D0=BA=D0=B8?='''
    eq_(u"Это сообщение с длинным сабжектом специально чтобы проверить кодировки", encodedword.mime_to_unicode(v))


def yahoo_encodings_test():
    v = '''
     =?utf-8?B?0K3RgtC+INGB0L7QvtCx0YnQtdC90LjQtSDRgSDQtNC70LjQvdC90YvQvCA=?=
      =?utf-8?B?0YHQsNCx0LbQtdC60YLQvtC8INGB0L/QtdGG0LjQsNC70YzQvdC+INGH0YI=?=
       =?utf-8?B?0L7QsdGLINC/0YDQvtCy0LXRgNC40YLRjCDQutC+0LTQuNGA0L7QstC60Lg=?='''
    eq_(u"Это сообщение с длинным сабжектом специально чтобы проверить кодировки", encodedword.mime_to_unicode(v))


def hotmail_encodings_test():
    v = ''' =?koi8-r?B?/NTPINPPz8LdxQ==?= =?koi8-r?B?zsnFINMgxMzJzg==?=
     =?koi8-r?B?ztnNINPBwtbFyw==?= =?koi8-r?B?1M/NINPQxcPJwQ==?=
      =?koi8-r?B?zNjOzyDe1M/C2Q==?= =?koi8-r?B?INDSz9fF0snU2A==?=
       =?koi8-r?B?IMvPxMnSz9fLyQ==?='''
    eq_(u"Это сообщение с длинным сабжектом специально чтобы проверить кодировки", encodedword.mime_to_unicode(v))


def various_encodings_test():
    v = '"=?utf-8?b?6ICD5Y+W5YiG5Lqr?=" <foo@example.com>'
    eq_(u'"考取分享" <foo@example.com>', encodedword.mime_to_unicode(v))

    v = """=?UTF-8?B?0JbQtdC60LA=?= <ev@mailgun.net>, =?UTF-8?B?0JrQvtC90YbQtdCy0L7QuQ==?= <eugueny@gmail.com>"""
    eq_(u"Жека <ev@mailgun.net>, Концевой <eugueny@gmail.com>", encodedword.mime_to_unicode(v))

    v = encodedword.mime_to_unicode("=?utf-8?b?0JrQvtC90YbQtdCy0L7QuQ==?= <ev@host.com>, Bob <bob@host.com>, =?utf-8?b?0JLQuNC90YE=?= <vince@host.com>")
    eq_(u"Концевой <ev@host.com>, Bob <bob@host.com>, Винс <vince@host.com>", v)

    v = '=?UTF-8?B?0J/RgNC+0LLQtdGA0Y/QtdC8INGA0YPRgdGB0LrQuNC1INGB0LDQsdC2?=\n =?UTF-8?B?0LXQutGC0Ysg0Lgg0Y7QvdC40LrQvtC0IOKYoA==?='
    eq_(u'Проверяем русские сабжекты и юникод ☠', encodedword.mime_to_unicode(v))

    v = '=?UTF-8?B?0J/RgNC+0LLQtdGA0Y/QtdC8INGA0YPRgdGB0LrQuNC1INGB0LDQsdC2?=\r\n =?UTF-8?B?0LXQutGC0Ysg0Lgg0Y7QvdC40LrQvtC0IOKYoA==?='
    eq_(u'Проверяем русские сабжекты и юникод ☠', encodedword.mime_to_unicode(v))

    v = u'=?utf-8?Q?Evaneos-Concepci=C3=B3n.pdf?='
    eq_(u'Evaneos-Concepción.pdf', encodedword.mime_to_unicode(v))


@patch.object(utils, '_guess_and_convert', Mock(side_effect=errors.EncodingError()))
def test_convert_to_utf8_unknown_encoding():
    v = "abc\x80def"
    eq_(u"abc\u20acdef", charsets.convert_to_unicode("windows-874", v))
    eq_(u"qwe", charsets.convert_to_unicode('X-UNKNOWN', u"qwe"))
    eq_(u"qwe", charsets.convert_to_unicode('ru_RU.KOI8-R', 'qwe'))
    eq_(u"qwe", charsets.convert_to_unicode('"utf-8"; format="flowed"', 'qwe'))

@patch.object(encodedword, 'unfold', Mock(side_effect=Exception))
def test_error_reporting():
    eq_("Sasha", encodedword.mime_to_unicode("Sasha"))
