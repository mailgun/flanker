from nose.tools import eq_

from flanker.mime import create, bounce
from tests import BOUNCE, SIGNED, BOUNCE_OFFICE365


def test_bounce_detect():
    for i, tc in enumerate([{
        'desc': 'Common bounce example',
        'mime': create.from_string(BOUNCE),
        'result': bounce.Result(
            score=1.875,
            status=u'5.1.1',
            notification=(
                    u"This is the mail system at host mail.example.com.\n\n"
                    u"I'm sorry to have to inform you that your message could not\n"
                    u"be delivered to one or more recipients. It's attached below.\n\n"
                    u"For further assistance, please send mail to postmaster.\n\n"
                    u"If you do so, please include this problem report. You can\n"
                    u"delete your own text from the attached returned message.\n\n"
                    u"                   The mail system\n\n"
                    u"<asdfasdfasdfasdfasdfasdfewrqertrtyrthsfgdfgadfqeadvxzvz@gmail.com>: host\n"
                    u"    gmail-smtp-in.l.google.com[209.85.210.17] said: 550-5.1.1 The email account\n"
                    u"    that you tried to reach does not exist. Please try 550-5.1.1\n"
                    u"    double-checking the recipient's email address for typos or 550-5.1.1\n"
                    u"    unnecessary spaces. Learn more at                              550 5.1.1\n"
                    u"    http://mail.google.com/support/bin/answer.py?answer=6596 17si20661415yxe.22\n"
                    u"    (in reply to RCPT TO command)\n"),
            diagnostic_code=(
                    u"smtp; 550-5.1.1 The email account that you tried to reach does"
                    u"    not exist. Please try 550-5.1.1 double-checking the recipient's email"
                    u"    address for typos or 550-5.1.1 unnecessary spaces. Learn more at"
                    u"    550 5.1.1 http://mail.google.com/support/bin/answer.py?answer=6596"
                    u"    17si20661415yxe.22")),
        'is_bounce': True
    }, {
        'desc': 'Office365 bounce messages lack Content-Description',
        'mime': create.from_string(BOUNCE_OFFICE365),
        'result': bounce.Result(
            score=1.25,
            status=u'5.1.10',
            notification=u'',
            diagnostic_code=(
                    u'smtp;550 5.1.10 RESOLVER.ADR.RecipientNotFound; '
                    u'Recipient noname@example.com not found by SMTP address lookup')),
        'is_bounce': True
    }, {
        'desc': 'Regular message',
        'mime': create.from_string(SIGNED),
        'result': bounce.Result(
            score=0.0,
            status=u'',
            notification=u'',
            diagnostic_code=u''),
        'is_bounce': False
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))

        # When
        result = bounce.detect(tc['mime'])

        # Then
        eq_(result, tc['result'])
        eq_(result.is_bounce(), tc['is_bounce'])
