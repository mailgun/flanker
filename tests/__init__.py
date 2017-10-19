# coding:utf-8

from os.path import join, abspath, dirname, exists
from nose.tools import *
import codecs


def fixtures_path():
    return join(abspath(dirname(__file__)), 'fixtures')


def fixture_file(name):
    return join(fixtures_path(), name)


def skip_if_asked():
    from nose import SkipTest
    import sys
    if '--no-skip' not in sys.argv:
        raise SkipTest()


def read_fixture_bytes(path):
    absolute_path = join(abspath(dirname(__file__)), 'fixtures', path)
    with open(absolute_path, 'rb') as f:
        return f.read()


# mime fixture files
BOUNCE = read_fixture_bytes('messages/bounce/zed.eml')
BOUNCE_OFFICE365 = read_fixture_bytes('messages/bounce/office365.eml')
MAILBOX_FULL = read_fixture_bytes('messages/bounce/mailbox-full.eml')
NDN = read_fixture_bytes('messages/bounce/delayed.eml')
NDN_BROKEN = read_fixture_bytes('messages/bounce/delayed-broken.eml')

SIGNED = read_fixture_bytes('messages/signed.eml')
LONG_LINKS = read_fixture_bytes('messages/long-links.eml')
MULTI_RECEIVED_HEADERS = read_fixture_bytes(
    'messages/multi-received-headers.eml')
MAILGUN_PNG = read_fixture_bytes('messages/attachments/mailgun.png')
MAILGUN_WAV = read_fixture_bytes('messages/attachments/mailgun-rocks.wav')

TORTURE = read_fixture_bytes('messages/torture.eml')
TORTURE_PART = read_fixture_bytes('messages/torture-part.eml')
BILINGUAL = read_fixture_bytes('messages/bilingual-simple.eml')
RELATIVE = read_fixture_bytes('messages/relative.eml')
IPHONE = read_fixture_bytes('messages/iphone.eml')

MULTIPART = read_fixture_bytes('messages/multipart.eml')
FROM_ENCODING = read_fixture_bytes('messages/from-encoding.eml')
NO_CTYPE = read_fixture_bytes('messages/no-ctype.eml')
APACHE_MIME_MESSAGE_NEWS = read_fixture_bytes(
    'messages/apache-message-news-mime.eml')
ENCLOSED = read_fixture_bytes('messages/enclosed.eml')
ENCLOSED_BROKEN_BOUNDARY = read_fixture_bytes('messages/enclosed-broken.eml')
ENCLOSED_ENDLESS = read_fixture_bytes('messages/enclosed-endless.eml')
ENCLOSED_BROKEN_BODY = read_fixture_bytes('messages/enclosed-broken-body.eml')
ENCLOSED_BROKEN_ENCODING = read_fixture_bytes(
    'messages/enclosed-bad-encoding.eml')
FALSE_MULTIPART = read_fixture_bytes('messages/false-multipart.eml')
ENCODED_HEADER = read_fixture_bytes('messages/encoded-header.eml')
MESSAGE_EXTERNAL_BODY= read_fixture_bytes(
    'messages/message-external-body.eml')
EIGHT_BIT = read_fixture_bytes('messages/8bitmime.eml')
BIG = read_fixture_bytes('messages/big.eml')
RUSSIAN_ATTACH_YAHOO = read_fixture_bytes(
    'messages/russian-attachment-yahoo.eml')
QUOTED_PRINTABLE = read_fixture_bytes('messages/quoted-printable.eml')
TEXT_ONLY = read_fixture_bytes('messages/text-only.eml')
MAILGUN_PIC = read_fixture_bytes('messages/mailgun-pic.eml')
BZ2_ATTACHMENT  = read_fixture_bytes('messages/bz2-attachment.eml')
OUTLOOK_EXPRESS = read_fixture_bytes('messages/outlook-express.eml')

AOL_FBL = read_fixture_bytes('messages/complaints/aol.eml')
YAHOO_FBL = read_fixture_bytes('messages/complaints/yahoo.eml')
NOTIFICATION = read_fixture_bytes('messages/bounce/no-mx.eml')
DASHED_BOUNDARIES = read_fixture_bytes('messages/dashed-boundaries.eml')
WEIRD_BOUNCE = read_fixture_bytes('messages/bounce/gmail-no-dns.eml')
WEIRD_BOUNCE_2 = read_fixture_bytes(
    'messages/bounce/gmail-invalid-address.eml')

WEIRD_BOUNCE_3 = read_fixture_bytes('messages/bounce/broken-mime.eml')
MISSING_BOUNDARIES = read_fixture_bytes('messages/missing-boundaries.eml')
MISSING_FINAL_BOUNDARY = read_fixture_bytes(
    'messages/missing-final-boundary.eml')
DISPOSITION_NOTIFICATION = read_fixture_bytes(
    'messages/disposition-notification.eml')
MAILFORMED_HEADERS = read_fixture_bytes('messages/mailformed-headers.eml')

SPAM_BROKEN_HEADERS = read_fixture_bytes('messages/spam/broken-headers.eml')
SPAM_BROKEN_CTYPE = read_fixture_bytes('messages/spam/broken-ctype.eml')
LONG_HEADER = read_fixture_bytes('messages/long-header.eml')
ATTACHED_PDF = read_fixture_bytes('messages/attached-pdf.eml')

# addresslib fixture files
MAILBOX_VALID_TESTS = read_fixture_bytes(
    'mailbox_valid.txt').decode('utf-8')
MAILBOX_INVALID_TESTS = read_fixture_bytes(
    'mailbox_invalid.txt').decode('utf-8')
ABRIDGED_LOCALPART_VALID_TESTS = read_fixture_bytes(
    'abridged_localpart_valid.txt').decode('utf-8')
ABRIDGED_LOCALPART_INVALID_TESTS = read_fixture_bytes(
    'abridged_localpart_invalid.txt').decode('utf-8')
URL_VALID_TESTS = read_fixture_bytes(
    'url_valid.txt').decode('utf-8')
URL_INVALID_TESTS = read_fixture_bytes(
    'url_invalid.txt').decode('utf-8')
DOMAIN_TYPO_VALID_TESTS = read_fixture_bytes(
    'domain_typos_valid.txt').decode('utf-8')
DOMAIN_TYPO_INVALID_TESTS = read_fixture_bytes(
    'domain_typos_invalid.txt').decode('utf-8')
