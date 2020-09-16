# coding:utf-8

"""
Public interface for flanker address (email or url) parsing and validation
capabilities.

Public Functions in flanker.addresslib.address module:

    * parse(address, addr_spec_only=False)

      Parse a single address or URL. Can parse just the address spec or the
      full mailbox.

    * parse_list(address_list, strict=False, as_tuple=False)

      Parse a list of addresses, operates in strict or relaxed modes. Strict
      mode will fail at the first instance of invalid grammar, relaxed modes
      tries to recover and continue.

    * validate_address(addr_spec)

      Validates (parse, plus dns, mx check, and custom grammar) a single
      address spec. In the case of a valid address returns an EmailAddress
      object, otherwise returns None.

    * validate_list(addr_list, as_tuple=False)

      Validates an address list, and returns a tuple of parsed and unparsed
      portions.

When valid addresses are returned, they are returned as an instance of either
EmailAddress or UrlAddress in flanker.addresslib.address.

See the parser.py module for implementation details of the parser.
"""
from logging import getLogger

import idna
import six
from idna import IDNAError
from ply.lex import LexError
from ply.yacc import YaccError
from six.moves.urllib_parse import urlparse
from time import time
from tld import get_tld

from flanker import _email
from flanker.addresslib._parser.lexer import lexer
from flanker.addresslib._parser.parser import (Mailbox, Url, mailbox_parser,
                                               mailbox_or_url_parser,
                                               mailbox_or_url_list_parser,
                                               addr_spec_parser, url_parser)
from flanker.addresslib.quote import smart_unquote, smart_quote
from flanker.addresslib.validate import (mail_exchanger_lookup,
                                         plugin_for_esp)
from flanker.mime.message.headers.encodedword import mime_to_unicode
from flanker.utils import is_pure_ascii, metrics_wrapper

_log = getLogger(__name__)

MAX_ADDRESS_LENGTH = 1024
MAX_ADDRESS_NUMBER = 1024
MAX_ADDRESS_LIST_LENGTH = MAX_ADDRESS_LENGTH * MAX_ADDRESS_NUMBER


@metrics_wrapper()
def parse(address, addr_spec_only=False, strict=False, metrics=False):
    """
    Given a string, returns a scalar object representing a single full
    mailbox (display name and addr-spec), addr-spec, or a url.

    If parsing the entire string fails and strict is not set to True, fall back
    to trying to parse the last word only and assume everything else is the
    display name.

    Returns an Address object and optionally metrics on processing
    time if requested.

    Examples:
        >>> address.parse('John Smith <john@smith.com')
        John Smith <john@smith.com>

        >>> print address.parse('John <john@smith.com>', addr_spec_only=True)
        None

        >>> print address.parse('john@smith.com', addr_spec_only=True)
        'john@smith.com'

        >>> address.parse('http://host.com/post?q')
        http://host.com/post?q

        >>> print address.parse('foo')
        None
    """
    mtimes = {'parsing': 0}
    if addr_spec_only:
        parser = addr_spec_parser
    else:
        parser = mailbox_or_url_parser

    address = _to_parser_input(address)

    # sanity checks
    if not address:
        return None, mtimes
    if len(address) > MAX_ADDRESS_LENGTH:
        _log.warning('address exceeds maximum length of %s', MAX_ADDRESS_LENGTH)
        return None, mtimes

    bstart = time()
    try:
        parse_rs = parser.parse(address.strip(), lexer=lexer.clone())
        addr_obj = _lift_parse_result(parse_rs)
    except (LexError, YaccError, SyntaxError):
        addr_obj = None

    if addr_obj is None and not strict:
        addr_parts = address.split(' ')
        addr_spec = addr_parts[-1]
        if len(addr_spec) < len(address):
            try:
                parse_rs = parser.parse(addr_spec, lexer=lexer.clone())
                addr_obj = _lift_parse_result(parse_rs)
                if addr_obj:
                    display_name = ' '.join(addr_parts[:-1])
                    if isinstance(display_name, six.binary_type):
                        display_name = display_name.decode('utf-8')
                    addr_obj._display_name = display_name

            except (LexError, YaccError, SyntaxError):
                addr_obj = None

    mtimes['parsing'] = time() - bstart
    return addr_obj, mtimes


@metrics_wrapper()
def parse_discrete_list(address_list, as_tuple=False, metrics=False):
    """
    Given an string, returns an AddressList object (an iterable list
    representing parsed email addresses and urls).

    Returns an AddressList object and optionally metrics on processing
    time if requested.

    Examples:
        >>> address.parse_list('A <a@b>')
        [A <a@b>]

        >>> address.parse_list('A <a@b>, C <d@e>')
        [A <a@b>, C <d@e>]

        >>> address.parse_list('A <a@b>, C, D <d@e>')
        None

        >>> address.parse_list('A <a@b>, D <d@e>, http://localhost')
        [A <a@b>, D <d@e>, http://localhost]
    """
    mtimes = {'parsing': 0}

    # Normalize the input to binary for Python 2, and text for Python 3.
    address_list_s = _to_parser_input(address_list)

    # sanity checks
    if not address_list_s:
        return _parse_list_result(as_tuple, AddressList(), [], mtimes)

    if len(address_list_s) > MAX_ADDRESS_LIST_LENGTH:
        _log.warning('address list exceeds maximum length of %s', MAX_ADDRESS_LIST_LENGTH)
        return _parse_list_result(as_tuple, AddressList(), [address_list], mtimes)

    bstart = time()
    try:
        parse_list_rs = mailbox_or_url_list_parser.parse(address_list_s.strip(),
                                                         lexer.clone())
        addr_list_obj, bad_addr_list = _lift_parse_list_result(parse_list_rs)
        if len(addr_list_obj) == 0:
            bad_addr_list.append(address_list_s)

        mtimes['parsing'] = time() - bstart
    except (LexError, YaccError, SyntaxError):
        return _parse_list_result(as_tuple, AddressList(), [address_list], mtimes)

    return _parse_list_result(as_tuple, addr_list_obj, bad_addr_list, mtimes)


@metrics_wrapper()
def parse_list(address_list, strict=False, as_tuple=False, metrics=False):
    """
    Given an string or list of email addresses and/or urls seperated by a
    delimiter (comma (,) or semi-colon (;)), returns an AddressList object
    (an iterable list representing parsed email addresses and urls).

    Given a list of email addresses, the strict parameter is passed to the
    parse call for each element. Given a string the strict parameter is
    ignored.

    The parser can return a list of parsed addresses or a tuple containing
    the parsed and unparsed portions. The parser also returns the parsing
    time metrics if requested.

    Examples:
        >>> address.parse_list('A <a@b>')
        [A <a@b>]

        >>> address.parse_list('A <a@b>, C <d@e>')
        [A <a@b>, C <d@e>]

        >>> address.parse_list('A <a@b>, C, D <d@e>')
        []

        >>> address.parse_list(['A <a@b>', 'C', 'D <d@e>'], as_tuple=True)
        ([A <a@b>, D <d@e>], ['C'])

        >>> address.parse_list('A <a@b>, D <d@e>, http://localhost')
        [A <a@b>, D <d@e>, http://localhost]
    """
    mtimes = {'parsing': 0}

    if not address_list:
        return _parse_list_result(as_tuple, AddressList(), [], mtimes)

    if isinstance(address_list, list):
        if len(address_list) > MAX_ADDRESS_NUMBER:
            _log.warning('address list exceeds maximum items of %s', MAX_ADDRESS_NUMBER)
            return _parse_list_result(as_tuple, AddressList(), [], mtimes)

        parsed, unparsed = AddressList(), []
        for address in address_list:
            if isinstance(address, six.string_types):
                addr_obj, metrics = parse(address, strict=strict, metrics=True)
                mtimes['parsing'] += metrics['parsing']
                if addr_obj:
                    parsed.append(addr_obj)
                else:
                    unparsed.append(address)
            elif isinstance(address, EmailAddress):
                parsed.append(address)
            elif isinstance(address, UrlAddress):
                parsed.append(address)
            else:
                unparsed.append(address)

        return _parse_list_result(as_tuple, parsed, unparsed, mtimes)

    if isinstance(address_list, six.string_types):
        if len(address_list) > MAX_ADDRESS_LIST_LENGTH:
            _log.warning('address list exceeds maximum length of %s', MAX_ADDRESS_LIST_LENGTH)
            return _parse_list_result(as_tuple, AddressList(), [address_list], mtimes)

        if not strict:
            _log.debug('relaxed parsing is not available for discrete lists, ignoring')

        return parse_discrete_list(address_list, as_tuple=as_tuple, metrics=True)

    return _parse_list_result(as_tuple, AddressList(), [address_list], mtimes)


@metrics_wrapper()
def validate_address(addr_spec, metrics=False, skip_remote_checks=False):
    """
    Given an addr-spec, runs the pre-parser, the parser, DNS MX checks,
    MX existence checks, and if available, ESP specific grammar for the
    local part.

    In the case of a valid address returns an EmailAddress object, otherwise
    returns None. If requested, will also return the parsing time metrics.

    Examples:
        >>> address.validate_address('john@non-existent-domain.com')
        None

        >>> address.validate_address('user@gmail.com')
        None

        >>> address.validate_address('user.1234@gmail.com')
        user.1234@gmail.com
    """
    mtimes = {'parsing': 0,
              'tld_lookup': 0,
              'mx_lookup': 0,
              'dns_lookup': 0,
              'mx_conn':0 ,
              'custom_grammar':0}

    # sanity check
    if addr_spec is None:
        return None, mtimes
    if '@' not in addr_spec:
        return None, mtimes

    # run parser against address
    bstart = time()
    paddr = parse(addr_spec, addr_spec_only=True, strict=True)
    mtimes['parsing'] = time() - bstart
    if paddr is None:
        _log.debug('failed parse check for %s', addr_spec)
        return None, mtimes

    # lookup the TLD
    bstart = time()
    tld = get_tld(paddr.hostname, fail_silently=True, fix_protocol=True)
    mtimes['tld_lookup'] = time() - bstart
    if tld is None:
        _log.debug('failed tld check for %s', addr_spec)
        return None, mtimes

    if skip_remote_checks:
        return paddr, mtimes

    # lookup if this domain has a mail exchanger
    exchanger, mx_metrics = mail_exchanger_lookup(paddr.hostname, metrics=True)
    if isinstance(exchanger, bytes):
        exchanger = exchanger.decode()
    mtimes['mx_lookup'] = mx_metrics['mx_lookup']
    mtimes['dns_lookup'] = mx_metrics['dns_lookup']
    mtimes['mx_conn'] = mx_metrics['mx_conn']
    if exchanger is None:
        _log.debug('failed mx check for %s', addr_spec)
        return None, mtimes

    # lookup custom local-part grammar if it exists
    bstart = time()
    plugin = plugin_for_esp(exchanger)
    mtimes['custom_grammar'] = time() - bstart
    if plugin and plugin.validate(paddr) is False:
        _log.debug('failed custom grammer check for %s/%s', addr_spec, plugin.__name__)
        return None, mtimes

    return paddr, mtimes


@metrics_wrapper()
def validate_list(addr_list, as_tuple=False, metrics=False, skip_remote_checks=False):
    """
    Validates an address list, and returns a tuple of parsed and unparsed
    portions.

    Returns results as a list or tuple consisting of the parsed addresses
    and unparsable protions. If requested, will also return parisng time
    metrics.

    Examples:
        >>> address.validate_address_list('a@mailgun.com, c@mailgun.com')
        [a@mailgun.com, c@mailgun.com]

        >>> address.validate_address_list('a@mailgun.com, b@example.com')
        [a@mailgun.com]

        >>> address.validate_address_list('a@b, c@d, e@example.com', as_tuple=True)
        ([a@mailgun.com, c@mailgun.com], ['e@example.com'])
    """
    mtimes = {'parsing': 0,
              'tld_lookup': 0,
              'mx_lookup': 0,
              'dns_lookup': 0,
              'mx_conn':0 ,
              'custom_grammar':0}

    # sanity check
    if not addr_list:
        return AddressList(), mtimes

    # run parser against address list
    bstart = time()
    parsed_addresses, unparseable = parse_list(addr_list, strict=True, as_tuple=True)
    mtimes['parsing'] = time() - bstart

    plist = AddressList()
    ulist = unparseable

    # validate each address
    for paddr in parsed_addresses:
        vaddr, metrics = validate_address(paddr.address, metrics=True, skip_remote_checks=skip_remote_checks)
        for k in mtimes.keys():
            mtimes[k] += metrics[k]
        if vaddr is None:
            ulist.append(paddr.full_spec())
        else:
            plist.append(paddr)

    if as_tuple:
        return plist, ulist, mtimes
    return plist, mtimes


def is_email(string):
    if parse(string, True):
        return True
    return False


class Address(object):
    """
    Base class that represents an address (email or URL). Use it to create
    concrete instances of different addresses:
    """

    @property
    def supports_routing(self):
        """
        Indicates that by default this address cannot be routed.
        """
        return False

    class Type(object):
        """
        Enumerates the types of addresses we support:
            >>> parse('foo@example.com').addr_type
            'email'

            >>> parse('http://example.com').addr_type
            'url'
        """
        Email = 'email'
        Url   = 'url'


class EmailAddress(Address):
    """
    Represents a fully parsed email address with built-in support for MIME
    encoding. Note, do not use EmailAddress class directly, use the parse()
    or parse_list() functions to return a scalar or iterable list respectively.

    Examples:
       >>> addr = parse("Bob Silva", "bob@host.com")
       >>> addr.address
       'bob@host.com'
       >>> addr.hostname
       'host.com'
       >>> addr.mailbox
       'bob'

    Display name is always returned in Unicode, i.e. ready to be displayed on
    web forms:

       >>> addr.display_name
       u'Bob Silva'

    And full email spec is always returned as a sting encoded for MIME:
       >>> addr.full_spec()
       'Bob Silva <bob@host.com>'
    """

    _addr_type = Address.Type.Email

    def __init__(self, raw_display_name=None, raw_addr_spec=None,
                 _display_name=None, _mailbox=None, _hostname=None):
        raw_display_name = _to_parser_input(raw_display_name)
        raw_addr_spec = _to_parser_input(raw_addr_spec)

        if raw_display_name and raw_addr_spec:
            mailbox = addr_spec_parser.parse(raw_addr_spec, lexer.clone())
            self._display_name = _to_text(raw_display_name)
            self._mailbox = _to_text(mailbox.local_part)
            self._hostname = _to_text(mailbox.domain)

        elif raw_display_name:
            mailbox = mailbox_parser.parse(raw_display_name, lexer.clone())
            self._display_name = _to_text(mailbox.display_name)
            self._mailbox = _to_text(mailbox.local_part)
            self._hostname = _to_text(mailbox.domain)

        elif raw_addr_spec:
            mailbox = addr_spec_parser.parse(raw_addr_spec, lexer.clone())
            self._display_name = u''
            self._mailbox = _to_text(mailbox.local_part)
            self._hostname = _to_text(mailbox.domain)

        elif _mailbox and _hostname:
            self._display_name = _display_name or u''
            self._mailbox = _mailbox
            self._hostname = _hostname

        else:
            raise SyntaxError('failed to create EmailAddress: bad parameters')

        # Convert display name to decoded unicode string.
        if (self._display_name.startswith('=?') and
                self._display_name.endswith('?=')):
            self._display_name = mime_to_unicode(self._display_name)
        if (self._display_name.startswith('"') and
                self._display_name.endswith('"') and
                len(self._display_name) > 2):
            self._display_name = smart_unquote(self._display_name)

        # Convert hostname to lowercase unicode string.
        self._hostname = self._hostname.lower()
        if self._hostname.startswith('xn--') or '.xn--' in self._hostname:
            self._hostname = idna.decode(self._hostname)
        if not is_pure_ascii(self._hostname):
            idna.encode(self._hostname)

        assert isinstance(self._display_name, six.text_type)
        assert isinstance(self._mailbox, six.text_type)
        assert isinstance(self._hostname, six.text_type)

    @property
    def addr_type(self):
        return self._addr_type

    @property
    def display_name(self):
        return self._display_name

    @property
    def ace_display_name(self):
        quoted_display_name = smart_quote(self._display_name)
        encoded_display_name = _email.encode_header(None, quoted_display_name,
                                                    'ascii', MAX_ADDRESS_LENGTH)
        return _to_str(encoded_display_name)

    @property
    def mailbox(self):
        return self._mailbox

    @property
    def hostname(self):
        return self._hostname

    @property
    def ace_hostname(self):
        return _to_str(idna.encode(self._hostname))

    @property
    def address(self):
        return u'{}@{}'.format(self._mailbox, self._hostname)

    @property
    def ace_address(self):
        if not is_pure_ascii(self._mailbox):
            raise ValueError('Address {} has no ASCII-compatable encoding'
                             .format(self.address))
        return _to_str('{}@{}'.format(self._mailbox, self.ace_hostname))

    @property
    def supports_routing(self):
        """
        Email addresses can be routed.
        """
        return True

    def __repr__(self):
        return _to_str(self.to_unicode())

    def __str__(self):
        return _to_str(self.address)

    def __unicode__(self):
        return self.to_unicode()

    def to_unicode(self):
        if self._display_name:
            return u'{} <{}@{}>'.format(smart_quote(self._display_name),
                                        self._mailbox, self._hostname)
        return u'{}@{}'.format(self._mailbox, self._hostname)

    def full_spec(self):
        """
        Returns an ASCII-compatable encoding of an email address or raises a
        ValueError. Display name and domain parts will be converted to
        ASCII-compatable encoding. The transformed address will be ASCII-only
        and RFC-2822 compliant.

           >>> EmailAddress("Ev K", "ev@example.com").full_spec()
           'Ev K <ev@example.com>'
           >>> EmailAddress("Жека", "ev@example.com").full_spec()
           '=?utf-8?b?0JbQtdC60LA=?= <ev@example.com>'
        """
        ace_address = self.ace_address
        if not self.display_name:
            return self.ace_address

        return '{} <{}>'.format(self.ace_display_name, ace_address)

    def contains_non_ascii(self):
        """
        Does the address contain any non-ASCII characters?
        """
        return not is_pure_ascii(self.address)

    def requires_non_ascii(self):
        """
        Can the address be converted to an ASCII compatible encoding?
        """
        if not is_pure_ascii(self.mailbox):
            return True
        if not is_pure_ascii(self.hostname):
            try:
                idna.encode(self.hostname)
            except idna.IDNAError:
                return True
        return False

    def contains_domain_literal(self):
        """
        Is the address a domain literal?
        """
        return self.hostname.startswith('[') and self.hostname.endswith(']')

    def __cmp__(self, other):
        return True

    def __eq__(self, other):
        """
        Allows comparison of two addresses.
        """
        if isinstance(other, six.string_types):
            other = parse(other)
        if other:
            return self.address.lower() == other.address.lower()
        return False

    def __ne__(self, other):
        """
        Negative comparison support
        """
        return not (self == other)

    def __hash__(self):
        """
        Hashing allows using Address objects as keys in collections and compare
        them in sets

            >>> a = Address.from_string("a@host")
            >>> b = Address.from_string("A <A@host>")
            >>> hash(a) == hash(b)
            True
            >>> s = set()
            >>> s.add(a)
            >>> s.add(b)
            >>> len(s)
            1
        """
        return hash(self.address.lower())


class UrlAddress(Address):
    """
    Represents a parsed URL:
        >>> url = parse("http://user@host.com:8080?q=a")
        >>> url.hostname
        'host.com'
        >>> url.port
        8080
        >>> url.scheme
        'http'
        >>> str(url)
        'http://user@host.com:8080?q=a'

    Note: do not create UrlAddress class directly by passing raw "internet
    data", use the parse() and parse_list() functions instead.
    """

    _address = None
    _addr_type = Address.Type.Url

    def __init__(self, raw=None, _address=None):

        if raw:
            raw = _to_parser_input(raw)
            url = url_parser.parse(raw, lexer.clone())
            self._address = urlparse(url.address)
        elif _address:
            self._address = urlparse(_address)
        else:
            raise SyntaxError('failed to create UrlAddress: bad parameters')

    @property
    def address(self):
        return self._address.geturl()

    @property
    def addr_type(self):
        return self._addr_type

    @property
    def hostname(self):
        hostname = self._address.hostname
        if hostname:
            return hostname.lower()
        else:
            return None

    @property
    def port(self):
        return self._address.port

    @property
    def scheme(self):
        return self._address.scheme

    @property
    def path(self):
        return self._address.path

    def __repr__(self):
        return _to_str(self.address)

    def __str__(self):
        return _to_str(self.address)

    def __unicode__(self):
        return self.address

    def to_unicode(self):
        return self.address

    def full_spec(self):
        return self.address

    def __eq__(self, other):
        if isinstance(other, six.string_types):
            other = parse(other)
        if other:
            return self.address == other.address
        return False

    def __hash__(self):
        return hash(self.address)


class AddressList(object):
    """
    Keeps the list of addresses. Each address is an EmailAddress or
    URLAddress objectAddress-derived object.

    To create a list, use the parse_list method, do not create an
    AddressList directly.

    To see if the address is in the list:
        >>> "missing@host.com" in al
        False
        >>> "bob@host.COM" in al
        True
    """

    def __init__(self, container=None):
        self._container = []
        if not container:
            return

        for i, addr in enumerate(container):
            if not isinstance(addr, Address):
                raise TypeError('Unexpected type %s in position %d'
                                % (type(addr), i))
            self._container.append(addr)

    def append(self, addr):
        if not isinstance(addr, Address):
            raise TypeError('Unexpected type %s' % type(addr))
        self._container.append(addr)

    def remove(self, addr):
        self._container.remove(addr)

    def __iter__(self):
        return iter(self._container)

    def __getitem__(self, key):
        return self._container[key]

    def __len__(self):
        return len(self._container)

    def __eq__(self, other):
        """
        When comparing ourselves to other lists we must ignore order.
        """
        if isinstance(other, (list, six.binary_type, six.text_type)):
            other = parse_list(other)
        if not isinstance(other, AddressList):
            raise TypeError('Cannot compare with %s' % type(other))
        return set(self._container) == set(other._container)

    def __repr__(self):
        return _to_str(''.join(['[', self.to_unicode(), ']']))

    def __str__(self):
        return _to_str(', '.join(addr.address for addr in self._container))

    def __unicode__(self):
        return self.to_unicode()

    def __add__(self, other):
        """
        Adding two AddressLists together yields another AddressList.
        """
        if isinstance(other, list):
            other = parse_list(other)

        if not isinstance(other, AddressList):
            raise TypeError('Cannot add %s' % type(other))

        container = self._container + other._container
        addr_lst = AddressList()
        addr_lst._container = container
        return addr_lst

    def full_spec(self, delimiter=', '):
        """
        Returns a full string which looks pretty much what the original was
        like
            >>> adl = AddressList("Foo <foo@host.com>, Bar <bar@host.com>")
            >>> adl.full_spec(delimiter='; ')
            'Foo <foo@host.com; Bar <bar@host.com>'
        """
        return delimiter.join(addr.full_spec() for addr in self._container)

    def to_unicode(self, delimiter=u', '):
        return delimiter.join(addr.to_unicode() for addr in self._container)

    def to_ascii_list(self):
        return [addr.full_spec() for addr in self._container]

    @property
    def addresses(self):
        """
        Returns a list of just addresses, i.e. no names:
            >>> adl = AddressList("Foo <foo@host.com>, Bar <bar@host.com>")
            >>> adl.addresses
            ['foo@host.com', 'bar@host.com']
        """
        return [addr.address for addr in self._container]

    @property
    def hostnames(self):
        """
        Returns a set of hostnames used in addresses in this list.
        """
        return set([addr.hostname for addr in self._container])

    @property
    def addr_types(self):
        """
        Returns a set of address types used in addresses in this list.
        """
        return set([addr.addr_type for addr in self._container])


def _lift_parse_result(parse_rs):
    if isinstance(parse_rs, Mailbox):
        try:
            return EmailAddress(
                _display_name=smart_unquote(_to_text(parse_rs.display_name)),
                _mailbox=_to_text(parse_rs.local_part),
                _hostname=_to_text(parse_rs.domain))
        except (UnicodeError, IDNAError):
            return None

    if isinstance(parse_rs, Url):
        return UrlAddress(_address=_to_text(parse_rs.address))

    return None


def _lift_parse_list_result(parse_list_rs):
    addr_list_obj = AddressList()
    bad_list = []
    for parse_rs in parse_list_rs:
        addr_obj = _lift_parse_result(parse_rs)
        if not addr_obj:
            if isinstance(parse_rs, Mailbox):
                bad_list.append(u'%s@%s' % (_to_text(parse_rs.local_part),
                                            _to_text(parse_rs.domain)))
            continue

        addr_list_obj.append(addr_obj)

    return addr_list_obj, bad_list


def _parse_list_result(as_tuple, parsed, unparsed, mtimes):
    if as_tuple:
        return parsed, unparsed, mtimes

    return parsed, mtimes


def _to_parser_input(parser_in):
    """
    Normalize the input to binary in Python 2, and text in Python 3.
    """
    if parser_in is None:
        return None

    if six.PY2:
        if isinstance(parser_in, six.text_type):
            parser_in = parser_in.encode('utf-8')
        assert isinstance(parser_in, six.binary_type), (
            'Expected %s, got %s' % (six.binary_type, type(parser_in)))
        return parser_in

    if isinstance(parser_in, six.binary_type):
        parser_in = parser_in.decode('utf-8')
    assert isinstance(parser_in, six.text_type), (
        'Expected %s, got %s' % (six.text_type, type(parser_in)))
    return parser_in


def _to_text(val):
    """
    Converts val to unicode in Python 2, and str in Python 3.
    """
    if val is None:
        return None

    if isinstance(val, six.binary_type):
        return val.decode('utf-8')

    if isinstance(val, six.text_type):
        return val

    raise TypeError('String type expected, got %s' % type(val))


def _to_str(val):
    """
    Converts val to str. Note that in different Python version the returned
    value has different semantic, and that is intentional.
    """
    if val is None:
        return None

    if isinstance(val, str):
        return val

    if six.PY2:
        return val.encode('utf-8')

    return val.decode('utf-8')
