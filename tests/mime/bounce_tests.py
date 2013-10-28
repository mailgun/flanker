from nose.tools import *
from .. import *
from flanker.mime import create

def test_bounce_analyzer_on_bounce():
    bm = create.from_string(BOUNCE)
    ok_(bm.is_bounce())
    eq_('5.1.1', bm.bounce.status)
    ok_(bm.bounce.diagnostic_code)


def test_bounce_analyzer_on_regular():
    bm = create.from_string(SIGNED)
    assert_false(bm.is_bounce())


def test_bounce_no_headers_error_message():
    msg = create.from_string("Nothing")
    assert_false(msg.is_bounce())
