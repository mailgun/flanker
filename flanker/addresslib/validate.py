# coding:utf-8

'''
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
'''

import re
import redis
import socket
import flanker.addresslib

from flanker.addresslib import corrector


def suggest_alternate(addr_spec):
    '''
    Given an addr-spec, suggests a alternate addr-spec if common spelling
    mistakes are detected in the domain portion.

    Returns an suggested alternate if one is found. Returns None if the
    address is invalid or no suggestions were found.

    Examples:
        >>> print validate.suggest_alternate('john@gmail.com')
        None
        >>> validate.suggest_alternate('john@gmail..com')
        'john@gmail.com'
    '''
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
    '''
    Preparses email addresses. Used to handle odd behavior by ESPs.
    '''
    # sanity check, ensure we have both local-part and domain
    parts = addr_spec.split('@')
    if len(parts) < 2:
        return None

    # if we add more esp specific checks, they should be done
    # with a dns lookup not string matching domain
    if parts[1] == 'gmail.com' or parts[1] == 'googlemail.com':
        parts[0] = parts[0].replace('.', '')

    return parts


def plugin_for_esp(mail_exchanger):
    '''
    Checks if custom grammar exists for a particular mail exchanger. If 
    a grammar is found, the plugin to validate an address for that particular
    email service provider is returned, otherwise None is returned.

    If you are adding the grammar for a email service provider, add the module
    to the flanker.addresslib.plugins directory then update the
    flanker.addresslib package to add it to the known list of custom grammars.
    '''
    for grammar in flanker.addresslib.CUSTOM_GRAMMAR_LIST:
        if grammar[0].match(mail_exchanger):
            return grammar[1]

    return None


def mail_exchanger_lookup(domain):
    '''
    Looks up the mail exchanger for a domain. If MX records exist they will
    be returned, if not it will attempt to fallback to A records, if neither
    exist None will be returned.

    Uses a cache to store the results of the mail exchanger lookup to speed
    up lookup times. The default is redis, but this can be overidden by your
    own cache as long as it conforms to the same interface as that of a dict.
    See the implimentation of the redis cache in the flanker.addresslib.driver
    package for more details if you wish to implement your own cache.

    The dnspython package is used for dns lookups. The dnspython package uses
    the dns server specified by your operating system. Just like the cache,
    this can be overridden by your own dns lookup method of choice as long
    as it conforms to the same interface as that of a dict. See the the
    implimentation of the dnspython lookup in the flanker.addresslib.driver
    package for more details.
    '''
    mx_cache = flanker.addresslib.mx_cache
    dns_lookup = flanker.addresslib.dns_lookup

    # if we have the mx lookup cached, return the cached result
    if mx_cache:
        lookup = mx_cache[domain]
        if lookup is not None:
            return (False, None) if lookup == 'False' else (True, lookup)

    # check if mx records exist
    fqdn = domain if domain[-1] == '.' else ''.join([domain, '.'])
    mx_hosts = dns_lookup[fqdn]
    if len(mx_hosts) == 0:
        mx_cache[domain] = False
        return (False, None)

    # check if we can connect to the mail exchanger
    mail_exchanger = connect_to_mail_exchanger(mx_hosts)
    if mail_exchanger is None:
        mx_cache[domain] = False
        return (False, None)

    # check if we can connect to the mail exchanger
    mail_exchanger = connect_to_mail_exchanger(mx_hosts)
    if mail_exchanger is None:
        mx_cache[domain] = False
        return (False, None)

    # valid mx records, connected to mail exchanger, return True
    mx_cache[domain] = mail_exchanger
    return (True, mail_exchanger)


def connect_to_mail_exchanger(mx_hosts):
    '''
    Given a list of MX hosts, attempts to connect to at least one on port 25.
    Returns the mail exchanger it was able to connect to or None.
    '''
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


ONE_WEEK = 604800
