# coding:utf-8

from os.path import join, abspath, dirname


def fixtures_path():
    return join(abspath(dirname(__file__)), 'fixtures')


def fixture_file(name):
    return join(fixtures_path(), name)


def skip_if_asked():
    from nose import SkipTest
    import sys
    if '--no-skip' not in sys.argv:
        raise SkipTest()


def read_fixture(path, binary=False):
    absolute_path = join(abspath(dirname(__file__)), 'fixtures', path)
    mode = 'rb' if binary else 'r'
    with open(absolute_path, mode) as f:
        content = f.read()

    if binary:
        return content

    # Normalize newline to be CRLF.
    content = content.replace('\r\n', '\n')
    content = content.replace('\r', '\n')
    content = content.replace('\n', '\r\n')
    return content


# mime fixture files
BOUNCE = read_fixture('messages/bounce/zed.eml')
BOUNCE_OFFICE365 = read_fixture('messages/bounce/office365.eml')
MAILBOX_FULL = read_fixture('messages/bounce/mailbox-full.eml')
NDN = read_fixture('messages/bounce/delayed.eml')
NDN_BROKEN = read_fixture('messages/bounce/delayed-broken.eml')

SIGNED = read_fixture('messages/signed.eml')
LONG_LINKS = read_fixture('messages/long-links.eml')
MULTI_RECEIVED_HEADERS = read_fixture(
    'messages/multi-received-headers.eml')
MAILGUN_PNG = read_fixture('messages/attachments/mailgun.png', binary=True)
MAILGUN_WAV = read_fixture('messages/attachments/mailgun-rocks.wav',
                           binary=True)

TORTURE = read_fixture('messages/torture.eml')
TORTURE_PART = read_fixture('messages/torture-part.eml')
BILINGUAL = read_fixture('messages/bilingual-simple.eml')
RELATIVE = read_fixture('messages/relative.eml')
IPHONE = read_fixture('messages/iphone.eml')

MULTIPART = read_fixture('messages/multipart.eml')
FROM_ENCODING = read_fixture('messages/from-encoding.eml', binary=True)
NO_CTYPE = read_fixture('messages/no-ctype.eml')
APACHE_MIME_MESSAGE_NEWS = read_fixture(
    'messages/apache-message-news-mime.eml')
ENCLOSED = read_fixture('messages/enclosed.eml')
ENCLOSED_BROKEN_BOUNDARY = read_fixture('messages/enclosed-broken.eml')
ENCLOSED_ENDLESS = read_fixture('messages/enclosed-endless.eml')
ENCLOSED_BROKEN_BODY = read_fixture('messages/enclosed-broken-body.eml')
ENCLOSED_BROKEN_ENCODING = read_fixture(
    'messages/enclosed-bad-encoding.eml', binary=True)
FALSE_MULTIPART = read_fixture('messages/false-multipart.eml')
ENCODED_HEADER = read_fixture('messages/encoded-header.eml')
MESSAGE_EXTERNAL_BODY= read_fixture(
    'messages/message-external-body.eml')
EIGHT_BIT = read_fixture('messages/8bitmime.eml')
BIG = read_fixture('messages/big.eml')
RUSSIAN_ATTACH_YAHOO = read_fixture(
    'messages/russian-attachment-yahoo.eml', binary=True)
QUOTED_PRINTABLE = read_fixture('messages/quoted-printable.eml')
TEXT_ONLY = read_fixture('messages/text-only.eml')
MAILGUN_PIC = read_fixture('messages/mailgun-pic.eml')
BZ2_ATTACHMENT  = read_fixture('messages/bz2-attachment.eml')
OUTLOOK_EXPRESS = read_fixture('messages/outlook-express.eml')

AOL_FBL = read_fixture('messages/complaints/aol.eml')
YAHOO_FBL = read_fixture('messages/complaints/yahoo.eml')
NOTIFICATION = read_fixture('messages/bounce/no-mx.eml')
DASHED_BOUNDARIES = read_fixture('messages/dashed-boundaries.eml')
WEIRD_BOUNCE = read_fixture('messages/bounce/gmail-no-dns.eml')
WEIRD_BOUNCE_2 = read_fixture(
    'messages/bounce/gmail-invalid-address.eml')

WEIRD_BOUNCE_3 = read_fixture('messages/bounce/broken-mime.eml')
MISSING_BOUNDARIES = read_fixture('messages/missing-boundaries.eml')
MISSING_FINAL_BOUNDARY = read_fixture(
    'messages/missing-final-boundary.eml')
DISPOSITION_NOTIFICATION = read_fixture(
    'messages/disposition-notification.eml')
MAILFORMED_HEADERS = read_fixture(
    'messages/mailformed-headers.eml', binary=True)
SPAM_BROKEN_HEADERS = read_fixture(
    'messages/spam/broken-headers.eml', binary=True)
SPAM_BROKEN_CTYPE = read_fixture('messages/spam/broken-ctype.eml')
LONG_HEADER = read_fixture('messages/long-header.eml')
ATTACHED_PDF = read_fixture('messages/attached-pdf.eml')

# addresslib fixture files
MAILBOX_VALID_TESTS = read_fixture('mailbox_valid.txt')
MAILBOX_INVALID_TESTS = read_fixture('mailbox_invalid.txt')
ABRIDGED_LOCALPART_VALID_TESTS = read_fixture('abridged_localpart_valid.txt')
ABRIDGED_LOCALPART_INVALID_TESTS = read_fixture(
    'abridged_localpart_invalid.txt')
URL_VALID_TESTS = read_fixture('url_valid.txt')
URL_INVALID_TESTS = read_fixture('url_invalid.txt')
DOMAIN_TYPO_VALID_TESTS = read_fixture('domain_typos_valid.txt')
DOMAIN_TYPO_INVALID_TESTS = read_fixture('domain_typos_invalid.txt')
