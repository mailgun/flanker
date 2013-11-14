'''
The flanker.addresslib package exposes a simple address parsing library that
can handle email addresses and urls.

See the address.py module for the public interfaces to the library and the
parser.py module for the implementation of the recursive decent parser
used to parse email addresses and urls.

To override the default DNS lookup library or MX Cache, use the
set_dns_lookup and set_mx_cache methods. For more details, see the User Manual.
'''
import re

from flanker.addresslib.drivers.redis_driver import RedisCache
from flanker.addresslib.drivers.dns_lookup import DNSLookup

from flanker.addresslib.plugins import yahoo
from flanker.addresslib.plugins import aol
from flanker.addresslib.plugins import gmail
from flanker.addresslib.plugins import icloud
from flanker.addresslib.plugins import hotmail
from flanker.addresslib.plugins import google


mx_cache = RedisCache()
dns_lookup = DNSLookup()

YAHOO_PATTERN = re.compile(r'''.*\.yahoodns\.net$''')
GMAIL_PATTERN = re.compile(r'''.*gmail-smtp-in\.l\.google.com$''')
AOL_PATTERN = re.compile(r'''.*\.mx\.aol\.com$''')
ICLOUD_PATTERN = re.compile(r'''.*\.icloud\.com\.akadns\.net$''')
HOTMAIL_PATTERN = re.compile(r'''mx[0-9]\.hotmail\.com''')
GOOGLE_PATTERN = re.compile(r'''(.*aspmx\.l\.google\.com$)|(aspmx.*\.googlemail.com$)''', re.IGNORECASE)

CUSTOM_GRAMMAR_LIST = [
    (YAHOO_PATTERN, yahoo),
    (GMAIL_PATTERN, gmail),
    (AOL_PATTERN, aol),
    (ICLOUD_PATTERN, icloud),
    (HOTMAIL_PATTERN, hotmail),
    (GOOGLE_PATTERN, google),
]

def set_dns_lookup(dlookup):
    global dns_lookup
    dns_lookup = dlookup

def set_mx_cache(mcache):
    global mx_cache
    mx_cache = mcache
