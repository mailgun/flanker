"""
The flanker.addresslib package exposes a simple address parsing library that
can handle email addresses and urls.

See the address.py module for the public interfaces to the library and the
parser.py module for the implementation of the recursive descent parser
used to parse email addresses and urls.

To override the default DNS lookup library or MX Cache, use the
set_dns_lookup and set_mx_cache methods. For more details, see the User Manual.
"""


def set_dns_lookup(dns_lookup):
    from flanker.addresslib import validate
    validate._dns_lookup = dns_lookup


def set_mx_cache(mx_cache):
    from flanker.addresslib import validate
    validate._mx_cache = mx_cache
