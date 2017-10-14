# coding:utf-8
from nose.tools import eq_

from flanker.mime.message.scanner import tokenize, ContentType, Boundary
from tests import (NO_CTYPE, EIGHT_BIT, TORTURE, BIG, DASHED_BOUNDARIES,
                   ATTACHED_PDF, ENCLOSED, NOTIFICATION)


_DUMMY = 0
C = ContentType
B = Boundary


def tokenizer_table_driven_test():
    for i, tc in enumerate([{
        'desc': 'We are ok, when there is no content type and boundaries',
        'mime': NO_CTYPE,
        'tokens': []
    }, {
        'desc': 'Can scan binary stuff: works for 8bit mime',
        'mime': EIGHT_BIT,
        'tokens': [
            C('multipart', 'alternative', dict(boundary="=-omjqkVTVbwdgCWFRgIkx")),
            B("=-omjqkVTVbwdgCWFRgIkx", _DUMMY, _DUMMY, False),
            C('text', 'plain', dict(charset="UTF-8")),
            B("=-omjqkVTVbwdgCWFRgIkx", _DUMMY, _DUMMY, False),
            C('text', 'html', dict(charset="utf-8")),
            B("=-omjqkVTVbwdgCWFRgIkx", _DUMMY, _DUMMY, True)
        ]
    }, {
        'desc': 'Boundary can contain `--`',
        'mime': BIG,
        'tokens': [
            C('multipart', 'mixed', dict(boundary="------------060808020401090407070006")),
            B("------------060808020401090407070006", _DUMMY, _DUMMY, False),
            C('text', 'html', dict(charset="ISO-8859-1")),
            B("------------060808020401090407070006", _DUMMY, _DUMMY, False),
            C('image', 'tiff', dict(name="teplosaurus-hi-res-02.tif")),
            B("------------060808020401090407070006", _DUMMY, _DUMMY, True)
        ]
    }, {
        'desc': 'Boundary can contain `--` at the end, even on boundaries other then the last one',
        'mime': DASHED_BOUNDARIES,
        'tokens': [
            C('multipart', 'alternative', dict(boundary="--120710081418BV.24190.Texte--")),
            B("--120710081418BV.24190.Texte--", _DUMMY, _DUMMY, False),
            C('text', 'plain', dict(charset="UTF-8")),
            B("--120710081418BV.24190.Texte--", _DUMMY, _DUMMY, False),
            C('text', 'html', dict(charset="UTF-8")),
            B("--120710081418BV.24190.Texte--", _DUMMY, _DUMMY, True)
        ]
    }, {
        'desc': 'Enclosed RFC-822 messages are properly identified',
        'mime': ENCLOSED,
        'tokens': [
            C('multipart', 'mixed', {'boundary': '===============6195527458677812340=='}),
            B('===============6195527458677812340==', 2567, 2608, final=False),
            C('text', 'plain', {'charset': 'us-ascii', 'format': 'flowed'}),
            B('===============6195527458677812340==', 2733, 2774, final=False),
            C('message', 'rfc822', {'name': 'thanks.eml'}),
            C('multipart', 'alternative', {'boundary': '===============4360815924781479146=='}),
            B('===============4360815924781479146==', 3792, 3833, final=False),
            C('text', 'plain', {'charset': 'utf-8'}),
            B('===============4360815924781479146==', 4323, 4364, final=False),
            C('text', 'html', {'charset': 'utf-8'}),
            B('===============4360815924781479146==', 5305, 5348, final=True),
            B('===============6195527458677812340==', 5347, 5390, final=True)
        ]
    }, {
        'desc': 'Content-Type from rfc822-headers part is retrieved',
        'mime': NOTIFICATION,
        'tokens': [
            C('multipart', 'report', {'boundary': 'CZz3eIzDbSJYu8fvbSlLFdH+/NwoCMV866Y+Iw==', 'report-type': 'delivery-status'}),
            B('CZz3eIzDbSJYu8fvbSlLFdH+/NwoCMV866Y+Iw==', 407, 450, final=False),
            C('text', 'plain', {}),
            B('CZz3eIzDbSJYu8fvbSlLFdH+/NwoCMV866Y+Iw==', 1090, 1133, final=False),
            C('message', 'delivery-status', {}),
            B('CZz3eIzDbSJYu8fvbSlLFdH+/NwoCMV866Y+Iw==', 1478, 1521, final=False),
            C('text', 'rfc822-headers', {}),
            C('multipart', 'alternative', {'boundary': '----=_NextPart_000_0000_01CD5B2E.428C0BF0'}),
            B('CZz3eIzDbSJYu8fvbSlLFdH+/NwoCMV866Y+Iw==', 2076, 2121, final=True)
        ]
    }, {
        'desc': 'Stress test',
        'mime': TORTURE,
        'tokens': [
            C('multipart', 'mixed', {'boundary': 'owatagusiam'}),
            B('owatagusiam', 389, 403, final=False),
            C('text', 'plain', {}),
            B('owatagusiam', 650, 664, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'alternative', {'boundary': 'Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk='}),
            B('Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk=', 2438, 2496, final=False),
            B('Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk=', 3249, 3307, final=False),
            C('multipart', 'mixed', {'boundary': 'Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2Yt1KaFdA'}),
            B('Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2Yt1KaFdA', 3410, 3470, final=False),
            C('text', 'richtext', {}),
            B('Alternative_Boundary_8dJn:mu0M2Yt5KaFZ8AdJn:mu0M2Yt1KaFdA', 4418, 4480, final=True),
            B('Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk=', 4481, 4539, final=False),
            C('application', 'andrew-inset', {}),
            B('Interpart_Boundary_AdJn:mu0M2YtJKaFh9AdJn:mu0M2YtJKaFk=', 5470, 5530, final=True),
            B('owatagusiam', 5531, 5545, final=False),
            C('message', 'rfc822', {}),
            C('audio', 'basic', {}),
            B('owatagusiam', 560278, 560292, final=False),
            C('audio', 'basic', {}),
            B('owatagusiam', 596156, 596170, final=False),
            C('image', 'pbm', {}),
            B('owatagusiam', 598054, 598068, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': 'Outermost_Trek'}),
            B('Outermost_Trek', 599955, 599972, final=False),
            C('multipart', 'mixed', {'boundary': 'Where_No_One_Has_Gone_Before'}),
            B('Where_No_One_Has_Gone_Before', 600041, 600072, final=False),
            B('Where_No_One_Has_Gone_Before', 600789, 600820, final=False),
            C('audio', 'x-sun', {}),
            B('Where_No_One_Has_Gone_Before', 631964, 631997, final=True),
            B('Outermost_Trek', 631997, 632014, final=False),
            C('multipart', 'mixed', {'boundary': 'Where_No_Man_Has_Gone_Before'}),
            B('Where_No_Man_Has_Gone_Before', 632083, 632114, final=False),
            C('image', 'gif', {}),
            B('Where_No_Man_Has_Gone_Before', 657860, 657891, final=False),
            C('image', 'gif', {}),
            B('Where_No_Man_Has_Gone_Before', 676411, 676442, final=False),
            C('application', 'x-be2', {'version': '12'}),
            B('Where_No_Man_Has_Gone_Before', 720176, 720207, final=False),
            C('application', 'atomicmail', {'version': '1.12'}),
            B('Where_No_Man_Has_Gone_Before', 729107, 729140, final=True),
            B('Outermost_Trek', 729140, 729157, final=False),
            C('audio', 'x-sun', {}),
            B('Outermost_Trek', 776430, 776449, final=True),
            B('owatagusiam', 776451, 776465, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': 'mail.sleepy.sau.144.8891'}),
            B('mail.sleepy.sau.144.8891', 777837, 777864, final=False),
            B('mail.sleepy.sau.144.8891', 777887, 777914, final=False),
            C('image', 'pgm', {}),
            B('mail.sleepy.sau.144.8891', 861843, 861870, final=False),
            B('mail.sleepy.sau.144.8891', 862131, 862160, final=True),
            B('owatagusiam', 862162, 862176, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': 'mail.sleepy.sau.158.532'}),
            B('mail.sleepy.sau.158.532', 863503, 863529, final=False),
            B('mail.sleepy.sau.158.532', 864751, 864777, final=False),
            C('image', 'pbm', {}),
            B('mail.sleepy.sau.158.532', 936251, 936279, final=True),
            B('owatagusiam', 936280, 936294, final=False),
            C('message', 'rfc822', {}),
            C('application', 'postscript', {}),
            B('owatagusiam', 1327932, 1327946, final=False),
            C('image', 'gif', {}),
            B('owatagusiam', 1405346, 1405360, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': 'hal_9000'}),
            B('hal_9000', 1406105, 1406116, final=False),
            C('audio', 'basic', {}),
            B('hal_9000', 1467518, 1467529, final=False),
            C('audio', 'basic', {}),
            B('hal_9000', 1507722, 1507735, final=True),
            B('owatagusiam', 1507735, 1507749, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': '16819560-2078917053-688350843:#11603'}),
            B('16819560-2078917053-688350843:#11603', 1508361, 1508400, final=False),
            C('application', 'postscript', {}),
            B('16819560-2078917053-688350843:#11603', 1560994, 1561033, final=False),
            C('application', 'octet-stream', {'name': 'Alices_PDP-10'}),
            B('16819560-2078917053-688350843:#11603', 1579392, 1579431, final=False),
            C('message', 'rfc822', {}),
            C('multipart', 'mixed', {'boundary': 'foobarbazola'}),
            B('foobarbazola', 1579725, 1579740, final=False),
            B('foobarbazola', 1580054, 1580069, final=False),
            C('multipart', 'parallel', {'boundary': 'seconddivider'}),
            B('seconddivider', 1580126, 1580142, final=False),
            C('image', 'gif', {}),
            B('seconddivider', 1583489, 1583505, final=False),
            C('audio', 'basic', {}),
            B('seconddivider', 1739502, 1739520, final=True),
            B('foobarbazola', 1739552, 1739567, final=False),
            C('application', 'atomicmail', {}),
            B('foobarbazola', 1744335, 1744350, final=False),
            C('message', 'rfc822', {}),
            C('audio', 'x-sun', {}),
            B('foobarbazola', 1819319, 1819336, final=True),
            B('16819560-2078917053-688350843:#11603', 1819336, 1819377, final=True),
            B('owatagusiam', 1819377, 1819393, final=True)
        ]
    }, {
        'desc': 'Content-Type headers in the multipart preamble and epilogue are ignored',
        'mime': ATTACHED_PDF,
        'tokens': [
            C('multipart', 'mixed', {'boundary': '_001_538f5bb0a7956_457a8046c758764ef_'}),
            B('_001_538f5bb0a7956_457a8046c758764ef_', 198, 238, final=False),
            C('multipart', 'alternative', {'boundary': '_000_538f5bb0a7956_457a8046c758764ef_'}),
            B('_000_538f5bb0a7956_457a8046c758764ef_', 479, 519, final=False),
            C('text', 'plain', {}),
            B('_000_538f5bb0a7956_457a8046c758764ef_', 567, 609, final=True),
            B('_001_538f5bb0a7956_457a8046c758764ef_', 685, 725, final=False),
            C('application', 'pdf', {'name': 'test.pdf'}),
            B('_001_538f5bb0a7956_457a8046c758764ef_', 10239, 10281, final=True)]
    }]):
        print('Test case #%d: %s' % (i, tc['desc']))

        # When
        tokens = tokenize(tc['mime'])

        # Then
        max_len = max(len(tc['tokens']), len(tokens))
        for expected_token, token in zip(
                tc['tokens'] + [''] * (max_len - len(tc['tokens'])),
                tokens + [''] * (max_len - len(tokens))):
            eq_(expected_token, token)
