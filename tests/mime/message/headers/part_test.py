# coding:utf-8

import flanker.mime.message.part as part
from nose.tools import eq_

STRINGS = (
    # Some normal strings
    ('', ''),
    ('hello', 'hello'),
    ('''hello
        there
        world''', '''hello
        there
        world'''),
    ('''hello
        there
        world
''', '''hello
        there
        world
'''),
    ('\201\202\203', '=81=82=83'),
    # Add some trailing MUST QUOTE strings
    ('hello ', 'hello=20'),
    ('hello\t', 'hello=09'),

    # Some long lines.  First, a single line of 108 characters
    ('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\xd8\xd9\xda\xdb\xdc\xdd\xde\xdfxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
     '''xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=D8=D9=DA=DB=DC=DD=DE=DFx=
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'''),

    # A line of exactly 76 characters, no soft line break should be needed
    ('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',
     'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'),

    # A line of 77 characters, forcing a soft line break at position 75,
    # and a second line of exactly 2 characters (because the soft line
    # break `=' sign counts against the line length limit).
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
     '''zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=
zz'''),

    # A line of 151 characters, forcing a soft line break at position 75,
    # with a second line of exactly 76 characters and no trailing =
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
     '''zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=
zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'''),

    # A string containing a hard line break, but which the first line is
    # 151 characters and the second line is exactly 76 characters.  This
    # should leave us with three lines, the first which has a soft line
    # break, and which the second and third do not.
    ('''yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz''',
     '''yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=
yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'''),

    # Lines that end with space or tab should be quoted
    ('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy ',
     '''yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=
=20'''),

    # Lines that end with a partial quoted character
    ('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=y',
    '''yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy=
=3Dy'''),

    # Lines that lead with a dot '.' should have the dot quoted
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.z',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Ez'),

    # Lines that end with a dot '.' are not quoted
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zz',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.=\n' +
     'zz'),

    # Lines that lead with a dot '.' should have the dot quoted and cut
    # if the quoted line is longer than 76 characters.
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Ezzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\nzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     'zz'),

    # Respect quoted characters when considering leading '.'
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2E=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=7F=\n' +
     '=7F=7F=7F'),

    # Should cut somewhere near the middle of the line
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat, quick hot dog, quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n'
     '=2Equick brown fox, quick brown cat, qui=\n' +
     'ck hot dog, quick read dog, quick whi=\n'
     + 'te bird'),

    # Respect quoted character when considering where to cut
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat\x7f\x7f\x7f\x7f\x7f, quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Equick brown fox, quick brown cat=7F=7F=\n' +
     '=7F=7F=7F, quick read dog, quick whi=\n' +
     'te bird'),

    # Avoid considering non quoted characters when cutting
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat=20=================, quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Equick brown fox, quick brown cat=3D20=\n' +
     '=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=3D=\n' +
     '=3D=3D=3D=3D=3D, quick read dog, quick white bird'),

    # Should quote leading '.' if the cut results in a '.' on the next line
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat..................... quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Equick brown fox, quick brown cat.....=\n' +
     '=2E............... quick read dog, quic=\n' +
     'k white bird'),

    # Should quote :space if the cut results in a :space at the end of the next line
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat                      quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Equick brown fox, quick brown cat    =20=\n' +
     '                 quick read dog, quic=\n' +
     'k white bird'),
    # Should quote :tab if the cut results in a :tab at the end of the next line
    ('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz' +
     '.quick brown fox, quick brown cat    \t                 quick read dog, quick white bird',
     'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz=\n' +
     '=2Equick brown fox, quick brown cat    =09=\n' +
     '                 quick read dog, quic=\n' +
     'k white bird'),
)


def test_encode():
    for p, e in STRINGS:
        enc = part._encode_transfer_encoding('quoted-printable', p)
        eq_(enc, e)

