# coding:utf-8
import zlib
from nose.tools import *
from mock import *
from flanker.mime.message.scanner import tokenize, ContentType, Boundary

from ... import *

C = ContentType
B = Boundary


def no_ctype_and_and_boundaries_test():
    """We are ok, when there is no content type and boundaries"""
    eq_([], tokenize(NO_CTYPE))


def binary_test():
    """Can scan binary stuff: works for 8bit mime"""
    tokens = tokenize(EIGHT_BIT)
    dummy = 0
    expect = [
        C('multipart', 'alternative', dict(boundary="=-omjqkVTVbwdgCWFRgIkx")),
        B("=-omjqkVTVbwdgCWFRgIkx", dummy, dummy, False),
        C('text', 'plain', dict(charset="UTF-8")),
        B("=-omjqkVTVbwdgCWFRgIkx", dummy, dummy, False),
        C('text', 'html', dict(charset="utf-8")),
        B("=-omjqkVTVbwdgCWFRgIkx", dummy, dummy, True)
        ]

    for a,b in zip(expect, tokens):
        eq_(a, b, "{0} != {1}".format(a, b))


def torture_test():
    """Torture is a complex multipart nested message"""

    tokens = tokenize(TORTURE)

    boundaries = set([b.value for b in tokens if b.is_boundary()])
    eq_(TORTURE_BOUNDARIES, boundaries)

    ctypes = [("{0}/{1}".format(b.main, b.sub), b.get_boundary())\
                  for b in tokens if b.is_content_type()]
    for a, b in zip(TORTURE_CTYPES, ctypes):
        eq_(a, b)


def dashed_boundary_test():
    """Make sure we don't screw up when boundary contains -- symbols,
    It's also awesome how fast we scan the 11MB message.
    """

    tokens = tokenize(BIG)
    dummy = 0
    expect = [
        C('multipart', 'mixed', dict(boundary="------------060808020401090407070006")),
        B("------------060808020401090407070006", dummy, dummy, False),
        C('text', 'html', dict(charset="ISO-8859-1")),
        B("------------060808020401090407070006", dummy, dummy, False),
        C('image', 'tiff', dict(name="teplosaurus-hi-res-02.tif")),
        B("------------060808020401090407070006", dummy, dummy, True)
        ]

    for a,b in zip(expect, tokens):
        eq_(a, b, "{0} != {1}".format(a, b))


def dashed_ending_boundary_test():
    """Make sure we don't screw up when boundary contains -- symbols at the
    ending as well"""

    tokens = tokenize(DASHED_BOUNDARIES)
    dummy = 0
    expect = [
        C('multipart', 'alternative', dict(boundary="--120710081418BV.24190.Texte--")),
        B("--120710081418BV.24190.Texte--", dummy, dummy, False),
        C('text', 'plain', dict(charset="UTF-8")),
        B("--120710081418BV.24190.Texte--", dummy, dummy, False),
        C('text', 'html', dict(charset="UTF-8")),
        B("--120710081418BV.24190.Texte--", dummy, dummy, True)
        ]

    for a,b in zip(expect, tokens):
        eq_(a, b, "{0} != {1}".format(a, b))


def complete_garbage_test():
    """ We survive complete garbage test """
    eq_([], tokenize(zlib.compress(NO_CTYPE)))



TORTURE_BOUNDARIES = set([
            'owatagusiam',
            'hal_9000',
            'Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk=',
            'Where_No_Man_Has_Gone_Before',
            'mail.sleepy.sau.158.532',
            'Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2Yt1KaFdA',
            '16819560-2078917053-688350843:#11603',
            'Where_No_One_Has_Gone_Before',
            'foobarbazola',
            'seconddivider',
            'mail.sleepy.sau.144.8891',
            'Outermost_Trek'
            ])

TORTURE_CTYPES = [
    ('multipart/mixed', 'owatagusiam'),
     ('text/plain', None),
     ('message/rfc822', None),
     ('multipart/alternative', 'Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk='),
     ('multipart/mixed', 'Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2Yt1KaFdA'),
     ('text/richtext', None),
     ('application/andrew-inset', None),
     ('message/rfc822', None),
     ('audio/basic', None),
     ('audio/basic', None),
     ('image/pbm', None),
     ('message/rfc822', None),
     ('multipart/mixed', 'Outermost_Trek'),
     ('multipart/mixed', 'Where_No_One_Has_Gone_Before'),
     ('audio/x-sun', None),
     ('multipart/mixed', 'Where_No_Man_Has_Gone_Before'),
     ('image/gif', None),
     ('image/gif', None),
     ('application/x-be2', None),
     ('application/atomicmail', None),
     ('audio/x-sun', None),
     ('message/rfc822', None),
     ('multipart/mixed', "mail.sleepy.sau.144.8891"),
     ('image/pgm', None),
     ('message/rfc822', None),
     ('multipart/mixed', "mail.sleepy.sau.158.532"),
     ('image/pbm', None),
     ('message/rfc822', None),
     ('application/postscript', None),
     ('image/gif', None),
     ('message/rfc822', None),
     ('multipart/mixed', 'hal_9000'),
     ('audio/basic', None),
     ('audio/basic', None),
     ('message/rfc822', None),
     ('multipart/mixed', '16819560-2078917053-688350843:#11603'),
     ('application/postscript', None),
     ('application/octet-stream', None),
     ('message/rfc822', None),
     ('multipart/mixed', 'foobarbazola'),
     ('multipart/parallel', 'seconddivider'),
     ('image/gif', None),
     ('audio/basic', None),
     ('application/atomicmail', None),
     ('message/rfc822', None),
     ('audio/x-sun', None)]
