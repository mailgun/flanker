from nose.tools import ok_, eq_, assert_false
from flanker.mime import create
from tests import BOUNCE, SIGNED


def test_bounce_analyzer_on_bounce():
    bm = create.from_string(BOUNCE)
    ok_(bm.is_bounce())
    eq_('5.1.1', bm.bounce.status)
    eq_('smtp; 550-5.1.1 The email account that you tried to reach does'
        '    not exist. Please try 550-5.1.1 double-checking the recipient\'s email'
        '    address for typos or 550-5.1.1 unnecessary spaces. Learn more at'
        '    550 5.1.1 http://mail.google.com/support/bin/answer.py?answer=6596'
        '    17si20661415yxe.22',
        bm.bounce.diagnostic_code)


def test_bounce_analyzer_on_regular():
    bm = create.from_string(SIGNED)
    assert_false(bm.is_bounce())


def test_bounce_no_headers_error_message():
    msg = create.from_string("Nothing")
    assert_false(msg.is_bounce())
