# coding:utf-8

from os.path import join, abspath, dirname, exists
from nose.tools import *
import codecs


def fixtures_path():
    return join(abspath(dirname(__file__)), "fixtures")

def fixture_file(name):
    return join(fixtures_path(), name)

def skip_if_asked():
    from nose import SkipTest
    import sys
    if "--no-skip" not in sys.argv:
        raise SkipTest()


# mime fixture files
BOUNCE = open(fixture_file("messages/bounce/zed.eml")).read()
MAILBOX_FULL = open(fixture_file("messages/bounce/mailbox-full.eml")).read()
NDN = open(fixture_file("messages/bounce/delayed.eml")).read()
NDN_BROKEN = open(fixture_file("messages/bounce/delayed-broken.eml")).read()

SIGNED_FILE = open(fixture_file("messages/signed.eml"))
SIGNED = open(fixture_file("messages/signed.eml")).read()
LONG_LINKS = open(fixture_file("messages/long-links.eml")).read()
MULTI_RECEIVED_HEADERS = open(
    fixture_file("messages/multi-received-headers.eml")).read()
MAILGUN_PNG = open(fixture_file("messages/attachments/mailgun.png")).read()
MAILGUN_WAV = open(
    fixture_file("messages/attachments/mailgun-rocks.wav")).read()

TORTURE = open(fixture_file("messages/torture.eml")).read()
TORTURE_PART = open(fixture_file("messages/torture-part.eml")).read()
BILINGUAL = open(fixture_file("messages/bilingual-simple.eml")).read()
RELATIVE = open(fixture_file("messages/relative.eml")).read()
IPHONE = open(fixture_file("messages/iphone.eml")).read()

MULTIPART = open(fixture_file("messages/multipart.eml")).read()
FROM_ENCODING = open(fixture_file("messages/from-encoding.eml")).read()
NO_CTYPE = open(fixture_file("messages/no-ctype.eml")).read()
APACHE_MIME_MESSAGE_NEWS = open(fixture_file("messages/apache-message-news-mime.eml")).read()
ENCLOSED = open(fixture_file("messages/enclosed.eml")).read()
ENCLOSED_BROKEN_BOUNDARY = open(
    fixture_file("messages/enclosed-broken.eml")).read()
ENCLOSED_ENDLESS = open(
    fixture_file("messages/enclosed-endless.eml")).read()
ENCLOSED_BROKEN_BODY = open(
    fixture_file("messages/enclosed-broken-body.eml")).read()
ENCLOSED_BROKEN_ENCODING = open(
    fixture_file("messages/enclosed-bad-encoding.eml")).read()
ENCODED_HEADER = open(
    fixture_file("messages/encoded-header.eml")).read()
MESSAGE_EXTERNAL_BODY= open(
    fixture_file("messages/message-external-body.eml")).read()
EIGHT_BIT = open(fixture_file("messages/8bitmime.eml")).read()
BIG = open(fixture_file("messages/big.eml")).read()
RUSSIAN_ATTACH_YAHOO = open(
    fixture_file("messages/russian-attachment-yahoo.eml")).read()
QUOTED_PRINTABLE = open(
    fixture_file("messages/quoted-printable.eml")).read()
TEXT_ONLY = open(fixture_file("messages/text-only.eml")).read()
MAILGUN_PIC = open(fixture_file("messages/mailgun-pic.eml")).read()
BZ2_ATTACHMENT  = open(fixture_file("messages/bz2-attachment.eml")).read()

AOL_FBL = open(fixture_file("messages/complaints/aol.eml")).read()
YAHOO_FBL = open(fixture_file("messages/complaints/yahoo.eml")).read()
NOTIFICATION = open(fixture_file("messages/bounce/no-mx.eml")).read()
DASHED_BOUNDARIES = open(
    fixture_file("messages/dashed-boundaries.eml")).read()
WEIRD_BOUNCE = open(fixture_file("messages/bounce/gmail-no-dns.eml")).read()
WEIRD_BOUNCE_2 = open(
    fixture_file("messages/bounce/gmail-invalid-address.eml")).read()

WEIRD_BOUNCE_3 = open(
    fixture_file("messages/bounce/broken-mime.eml")).read()
MISSING_BOUNDARIES = open(
    fixture_file("messages/missing-boundaries.eml")).read()
MISSING_FINAL_BOUNDARY = open(
    fixture_file("messages/missing-final-boundary.eml")).read()
DISPOSITION_NOTIFICATION = open(
    fixture_file("messages/disposition-notification.eml")).read()
MAILFORMED_HEADERS = open(
    fixture_file("messages/mailformed-headers.eml")).read()

SPAM_BROKEN_HEADERS = open(
    fixture_file("messages/spam/broken-headers.eml")).read()
SPAM_BROKEN_CTYPE = open(
    fixture_file("messages/spam/broken-ctype.eml")).read()
LONG_HEADER = open(
    fixture_file("messages/long-header.eml")).read()
ATTACHED_PDF = open(fixture_file("messages/attached-pdf.eml")).read()



# addresslib fixture files
MAILBOX_VALID_TESTS = open(fixture_file("mailbox_valid.txt")).read()
MAILBOX_INVALID_TESTS = open(fixture_file("mailbox_invalid.txt")).read()
ABRIDGED_LOCALPART_VALID_TESTS = open(fixture_file("abridged_localpart_valid.txt")).read()
ABRIDGED_LOCALPART_INVALID_TESTS = open(fixture_file("abridged_localpart_invalid.txt")).read()
URL_VALID_TESTS = codecs.open(fixture_file("url_valid.txt"), encoding='utf-8', mode='r').read()
URL_INVALID_TESTS = codecs.open(fixture_file("url_invalid.txt"), encoding='utf-8', mode='r').read()

DOMAIN_TYPO_VALID_TESTS = open(fixture_file("domain_typos_valid.txt")).read()
DOMAIN_TYPO_INVALID_TESTS = open(fixture_file("domain_typos_invalid.txt")).read()
