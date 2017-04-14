# coding:utf-8

"""
Validation module that that supports alternate spelling suggestions for
domains, MX record lookup and query, as well as custom local-part grammar for
large ESPs.

This module should probably not be used directly, use
flanker.addresslib.address unles you are building ontop of the library.

Public Functions in flanker.addresslib.validate module:

    * suggest_alternate(addr_spec)

      Given an addr-spec, suggests an alternate if a typo is found. Returns
      None if no alternate is suggested.

    * preparse_address(addr_spec)

      Preparses email addresses. Used to handle odd behavior by ESPs.

    * plugin_for_esp(mail_exchanger)

      Looks up the custom grammar plugin for a given ESP via the mail
      exchanger.

    * mail_exchanger_lookup(domain)

      Looks up the mail exchanger for a given domain.

    * connect_to_mail_exchanger(mx_hosts)

      Attempts to connect to a given mail exchanger to see if it exists.
"""
import socket
import time

import regex as re
from logging import getLogger

from flanker.addresslib import corrector
from flanker.addresslib.plugins import aol
from flanker.addresslib.plugins import gmail
from flanker.addresslib.plugins import google
from flanker.addresslib.plugins import hotmail
from flanker.addresslib.plugins import icloud
from flanker.addresslib.plugins import yahoo
from flanker.utils import metrics_wrapper

log = getLogger(__name__)

_YAHOO_PATTERN = re.compile(r'''mta[0-9]+\.am[0-9]+\.yahoodns\.net$''')
_GMAIL_PATTERN = re.compile(r'''.*gmail-smtp-in\.l\.google.com$''')
_AOL_PATTERN = re.compile(r'''.*\.mx\.aol\.com$''')
_ICLOUD_PATTERN = re.compile(r'''.*\.mail\.icloud\.com$''')
_HOTMAIL_PATTERN = re.compile(r'''mx[0-9]\.hotmail\.com''')
_GOOGLE_PATTERN = re.compile(r'''(.*aspmx\.l\.google\.com$)|(aspmx.*\.googlemail.com$)''', re.IGNORECASE)

_CUSTOM_GRAMMAR_LIST = [
    (_YAHOO_PATTERN, yahoo),
    (_GMAIL_PATTERN, gmail),
    (_AOL_PATTERN, aol),
    (_ICLOUD_PATTERN, icloud),
    (_HOTMAIL_PATTERN, hotmail),
    (_GOOGLE_PATTERN, google),
]

_mx_cache = None
_dns_lookup = None


def suggest_alternate(addr_spec):
    """
    Given an addr-spec, suggests a alternate addr-spec if common spelling
    mistakes are detected in the domain portion.

    Returns an suggested alternate if one is found. Returns None if the
    address is invalid or no suggestions were found.

    Examples:
        >>> print validate.suggest_alternate('john@gmail.com')
        None
        >>> validate.suggest_alternate('john@gmail..com')
        'john@gmail.com'
    """
    # sanity check
    if addr_spec is None:
        return None

    # preparse address into its parts and perform any ESP specific preparsing
    addr_parts = preparse_address(addr_spec)
    if addr_parts is None:
        return None

    # correct spelling
    sugg_domain = corrector.suggest(addr_parts[-1])

    # if suggested domain is the same as the passed in domain
    # don't return any suggestions
    if sugg_domain == addr_parts[-1]:
        return None

    return '@'.join([addr_parts[0], sugg_domain])


def preparse_address(addr_spec):
    """
    Preparses email addresses. Used to handle odd behavior by ESPs.
    """
    # sanity check, ensure we have both local-part and domain
    parts = addr_spec.split('@')
    if len(parts) < 2:
        return None

    return parts


def plugin_for_esp(mail_exchanger):
    """
    Checks if custom grammar exists for a particular mail exchanger. If
    a grammar is found, the plugin to validate an address for that particular
    email service provider is returned, otherwise None is returned.

    If you are adding the grammar for a email service provider, add the module
    to the flanker.addresslib.plugins directory then update the
    flanker.addresslib package to add it to the known list of custom grammars.
    """
    for grammar in _CUSTOM_GRAMMAR_LIST:
        if grammar[0].match(mail_exchanger):
            return grammar[1]

    return None


@metrics_wrapper()
def mail_exchanger_lookup(domain, metrics=False):
    """
    Looks up the mail exchanger for a domain. If MX records exist they will
    be returned, if not it will attempt to fallback to A records, if neither
    exist None will be returned.
    """
    mtimes = {'mx_lookup': 0, 'dns_lookup': 0, 'mx_conn': 0}

    # look in cache
    bstart = time.time()
    in_cache, cache_value = lookup_exchanger_in_cache(domain)
    mtimes['mx_lookup'] = time.time() - bstart
    if in_cache:
        return cache_value, mtimes

    # dns lookup on domain
    if domain.startswith('[') and domain.endswith(']'):
        mx_hosts = [domain[1:-1]]
    else:
        bstart = time.time()
        mx_hosts = lookup_domain(domain)
        mtimes['dns_lookup'] = time.time() - bstart
        if mx_hosts is None:
            # try one more time
            bstart = time.time()
            mx_hosts = lookup_domain(domain)
            mtimes['dns_lookup'] += time.time() - bstart
            if mx_hosts is None:
                log.warning('failed mx lookup for %s', domain)
                return None, mtimes

    # test connecting to the mx exchanger
    bstart = time.time()
    mail_exchanger = connect_to_mail_exchanger(mx_hosts)
    mtimes['mx_conn'] = time.time() - bstart
    if mail_exchanger is None:
        log.warning('failed mx connection for %s/%s', domain, mx_hosts)
        return None, mtimes

    # valid mx records, connected to mail exchanger, return True
    _get_mx_cache()[domain] = mail_exchanger
    return mail_exchanger, mtimes


def lookup_exchanger_in_cache(domain):
    """
    Uses a cache to store the results of the mail exchanger lookup to speed
    up lookup times. The default is redis, but this can be overidden by your
    own cache as long as it conforms to the same interface as that of a dict.
    See the implimentation of the redis cache in the flanker.addresslib.driver
    package for more details if you wish to implement your own cache.
    """
    lookup = _get_mx_cache()[domain]
    if lookup is None:
        return (False, None)

    if lookup == 'False':
        return (True, None)
    else:
        return (True, lookup)


def lookup_domain(domain):
    """
    The dnspython package is used for dns lookups. The dnspython package uses
    the dns server specified by your operating system. Just like the cache,
    this can be overridden by your own dns lookup method of choice as long
    as it conforms to the same interface as that of a dict. See the the
    implimentation of the dnspython lookup in the flanker.addresslib.driver
    package for more details.
    """
    fqdn = domain if domain[-1] == '.' else ''.join([domain, '.'])
    mx_hosts = _get_dns_lookup()[fqdn]

    if len(mx_hosts) == 0:
        return None
    return mx_hosts


def connect_to_mail_exchanger(mx_hosts):
    """
    Given a list of MX hosts, attempts to connect to at least one on port 25.
    Returns the mail exchanger it was able to connect to or None.
    """
    for host in mx_hosts:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((host, 25))
            s.close()
            return host
        except:
            continue

    return None


def _get_mx_cache():
    global _mx_cache
    if _mx_cache is None:
        from flanker.addresslib.drivers.redis_driver import RedisCache
        _mx_cache = RedisCache()

    return _mx_cache


def _get_dns_lookup():
    global _dns_lookup
    if _dns_lookup is None:
        from flanker.addresslib.drivers.dns_lookup import DNSLookup
        _dns_lookup = DNSLookup()

    return _dns_lookup
