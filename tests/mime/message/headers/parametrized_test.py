# coding:utf-8

from nose.tools import *
from mock import *
from flanker.mime.message.headers import parametrized

def old_style_test_google():
    h = """image/png;
	name="=?KOI8-R?B?68HS1MnOy8Eg0yDP3sXO2Cwgz97FztggxMzJzs7ZzSA=?=
	=?KOI8-R?B?0NLFxMzJzs7ZzSDJzcXOxc0g0NLFyc3FzsXNINTByw==?=
	=?KOI8-R?B?yc0g3tTPINTP3s7PINrBys3F1CDU1d7VINDSxdTV3tUg?=
	=?KOI8-R?B?zcXT1MEg0NLT1M8gz8bJx8XU2C5wbmc=?="""
    eq_(('image/png', {'name': u'Картинка с очень, очень длинным предлинным именем преименем таким что точно займет тучу претучу места прсто офигеть.png'}), parametrized.decode(h))


def old_style_test_aol():
    h = '''image/png; name="=?utf-8?Q?=D0=9A=D0=B0=D1=80=D1=82=D0=B8=D0=BD=D0=BA=D0=B0_=D1=81_?=
 =?utf-8?Q?=D0=BE=D1=87=D0=B5=D0=BD=D1=8C,_=D0=BE=D1=87=D0=B5=D0=BD?=
 =?utf-8?Q?=D1=8C_=D0=B4=D0=BB=D0=B8=D0=BD=D0=BD=D1=8B=D0=BC_=D0=BF?=
 =?utf-8?Q?=D1=80=D0=B5=D0=B4=D0=BB=D0=B8=D0=BD=D0=BD=D1=8B=D0=BC_=D0=B8?=
 =?utf-8?Q?=D0=BC=D0=B5=D0=BD=D0=B5=D0=BC_=D0=BF=D1=80=D0=B5=D0=B8=D0=BC?=
 =?utf-8?Q?=D0=B5=D0=BD=D0=B5=D0=BC_=D1=82=D0=B0=D0=BA=D0=B8=D0=BC_?=
 =?utf-8?Q?=D1=87=D1=82=D0=BE_=D1=82=D0=BE=D1=87=D0=BD=D0=BE_=D0=B7?=
 =?utf-8?Q?=D0=B0=D0=B9=D0=BC=D0=B5=D1=82_=D1=82=D1=83=D1=87=D1=83_?=
 =?utf-8?Q?=D0=BF=D1=80=D0=B5=D1=82=D1=83=D1=87=D1=83_=D0=BC=D0=B5=D1=81?=
 =?utf-8?Q?=D1=82=D0=B0_=D0=BF=D1=80=D1=81=D1=82=D0=BE_=D0=BE=D1=84?=
 =?utf-8?Q?=D0=B8=D0=B3=D0=B5=D1=82=D1=8C.png?="'''
    eq_(('image/png', {'name': u'Картинка с очень, очень длинным предлинным именем преименем таким что точно займет тучу претучу места прсто офигеть.png'}), parametrized.decode(h))


def new_style_test():
    # missing ;
    h = ''' application/x-stuff
    title*0*=us-ascii'en'This%20is%20even%20more%20
    title*1*=%2A%2A%2Afun%2A%2A%2A%20
    title*2="isn't it!"'''
    eq_(('application/x-stuff', {'title': u"This is even more ***fun*** isn't it!"}), parametrized.decode(h))

    h = '''message/external-body; access-type=URL;
         URL*0="ftp://";
         URL*1="cs.utk.edu/pub/moore/bulk-mailer/bulk-mailer.tar"'''
    eq_(('message/external-body', {'access-type': 'URL', 'url': u"ftp://cs.utk.edu/pub/moore/bulk-mailer/bulk-mailer.tar"}), parametrized.decode(h))


    h = '''application/x-stuff;
         title*=us-ascii'en-us'This%20is%20%2A%2A%2Afun%2A%2A%2A'''
    eq_(('application/x-stuff', {'title': u"This is ***fun***"}),
        parametrized.decode(h))


def simple_test():
    eq_(("message/rfc822", {}), parametrized.decode("MESSAGE/RFC822"))
    eq_(("text/plain", {}), parametrized.decode("text/plain (this is text)"))


def broken_test():
    eq_((None, {}), parametrized.decode(""))


def content_types_test():
    eq_(('binary', {'name': 'Alices_PDP-10'}), parametrized.decode('''BINARY;name="Alices_PDP-10"'''))
    eq_(('multipart/mixed', {'boundary': 'mail.sleepy.sau.158.532'}), parametrized.decode('''MULTIPART/MIXED;boundary="mail.sleepy.sau.158.532"'''))
    eq_(('multipart/mixed', {'boundary': 'Where_No_Man_Has_Gone_Before'}), parametrized.decode('''MULTIPART/MIXED;boundary=Where_No_Man_Has_Gone_Before'''))
    eq_(('multipart/mixed', {'boundary': 'Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2=Yt1KaFdA'}), parametrized.decode(''' multipart/mixed; \n\tboundary="Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2=Yt1KaFdA"'''))
    eq_(('multipart/mixed', {'boundary': '16819560-2078917053-688350843:#11603'}), parametrized.decode('''MULTIPART/MIXED;BOUNDARY="16819560-2078917053-688350843:#11603"'''))

def content_type_param_with_spaces_test():
    eq_(('multipart/alternative',{'boundary':'nextPart'}), parametrized.decode("multipart/alternative; boundary = nextPart"))
