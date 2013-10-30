# coding:utf-8

'''
_AddressParser is an implementation of a recursive decent parser for email
addresses and urls. While _AddressParser can be used directly it is not
recommended, use the the parse() and parse_list() methods which are provided
in the address module for convenience.

The grammar supported by the parser (as well as other limitations) are
outlined below. Plugins are also supported to allow for custom more
restrictive grammar that is typically seen at large Email Service Providers
(ESPs).

For email addresses, the grammar tries to stick to RFC 5322 as much as
possible, but includes relaxed (lax) grammar as well to support for common
realistic uses of email addresses on the Internet.

Grammar:


    address-list      ->    address { delimiter address }
    mailbox           ->    name-addr-rfc | name-addr-lax | addr-spec | url

    name-addr-rfc     ->    [ display-name-rfc ] angle-addr-rfc
    display-name-rfc  ->    [ whitespace ] word { whitespace word }
    angle-addr-rfc    ->    [ whitespace ] < addr-spec > [ whitespace ]

    name-addr-lax     ->    [ display-name-lax ] angle-addr-lax
    display-name-lax  ->    [ whitespace ] word { whitespace word } whitespace
    angle-addr-lax    ->    addr-spec [ whitespace ]

    addr-spec         ->    [ whitespace ] local-part @ domain [ whitespace ]
    local-part        ->    dot-atom | quoted-string
    domain            ->    dot-atom

    word              ->    word-ascii | word-unicode
    word-ascii        ->    atom | quoted-string
    word-unicode      ->    unicode-atom | unicode-qstring
    whitespace        ->    whitespace-ascii | whitespace-unicode


Additional limitations on email addresses:

    1. local-part:
        * Must not be greater than 64 octets

    2. domain:
        * No more than 127 levels
        * Each level no more than 63 octets
        * Texual representation can not exceed 253 characters
        * No level can being or end with -

    3. Maximum mailbox length is len(local-part) + len('@') + len(domain) which
       is 64 + 1 + 253 = 318 characters. Allow 194 characters for a display
       name and the (very generous) limit becomes 512 characters. Allow 1024
       mailboxes and the total limit on a mailbox-list is 524288 characters.
'''

import re
import flanker.addresslib.address

from flanker.addresslib.tokenizer import TokenStream
from flanker.addresslib.tokenizer import LBRACKET
from flanker.addresslib.tokenizer import AT_SYMBOL
from flanker.addresslib.tokenizer import RBRACKET
from flanker.addresslib.tokenizer import DQUOTE
from flanker.addresslib.tokenizer import BAD_DOMAIN
from flanker.addresslib.tokenizer import DELIMITER
from flanker.addresslib.tokenizer import WHITESPACE
from flanker.addresslib.tokenizer import UNI_WHITE
from flanker.addresslib.tokenizer import ATOM
from flanker.addresslib.tokenizer import UNI_ATOM
from flanker.addresslib.tokenizer import UNI_QSTR
from flanker.addresslib.tokenizer import DOT_ATOM
from flanker.addresslib.tokenizer import QSTRING
from flanker.addresslib.tokenizer import URL

from flanker.mime.message.headers.encoding import encode_string

from flanker.utils import is_pure_ascii
from flanker.utils import contains_control_chars
from flanker.utils import cleanup_display_name
from flanker.utils import cleanup_email
from flanker.utils import to_utf8


class _AddressParser(object):
    '''
    Do not use _AddressParser directly because it heavily relies on other
    private classes and methods and it's interface is not guarenteed, it
    will change in the future and possibly break your application.

    Instead use the parse() and parse_list() functions in the address.py
    module which will always return a scalar or iterable respectively.
    '''

    def __init__(self, strict=False):
        self.stream = None
        self.strict = strict

    def address_list(self, stream):
        '''
        Extract a mailbox and/or url list from a stream of input, operates in
        strict and relaxed modes.
        '''
        # sanity check
        if not stream:
            raise ParserException('No input provided to parser.')

        # to avoid spinning here forever, limit address list length
        if len(stream) > MAX_ADDRESS_LIST_LENGTH:
            raise ParserException('Stream length exceeds maximum allowable ' + \
                'address list length of ' + str(MAX_ADDRESS_LIST_LENGTH) + '.')

        # set stream
        self.stream = TokenStream(stream)

        if self.strict is True:
            return self._address_list_strict()
        return self._address_list_relaxed()

    def address(self, stream):
        '''
        Extract a single address or url from a stream of input, always
        operates in strict mode.
        '''
        # sanity check
        if not stream:
            raise ParserException('No input provided to parser.')

        # to avoid spinning here forever, limit mailbox length
        if len(stream) > MAX_ADDRESS_LENGTH:
            raise ParserException('Stream length exceeds maximum allowable ' + \
                'address length of ' + str(MAX_ADDRESS_LENGTH) + '.')

        self.stream = TokenStream(stream)

        addr = self._address()
        if addr:
            # optional whitespace
            self._whitespace()

            # if we hit the end of the stream, we have a valid inbox
            if self.stream.end_of_stream():
                return addr

        return None

    def address_spec(self, stream):
        '''
        Extract a single address spec from a stream of input, always
        operates in strict mode.
        '''
        # sanity check
        if stream is None:
            raise ParserException('No input provided to parser.')

        # to avoid spinning here forever, limit mailbox length
        if len(stream) > MAX_ADDRESS_LENGTH:
            raise ParserException('Stream length exceeds maximum allowable ' + \
                'address length of ' + str(MAX_ADDRESS_LENGTH) + '.')

        self.stream = TokenStream(stream)

        addr = self._addr_spec()
        if addr:
            # optional whitespace
            self._whitespace()

            # if we hit the end of the stream, we have a valid inbox
            if self.stream.end_of_stream():
                return addr

        return None

    def _mailbox_post_processing_checks(self, address):
        "Additional post processing checks to ensure mailbox is valid."
        parts = address.split('@')

        # check if local part is less than 128 octets, the actual
        # limit is 64 octets but we double the size here because
        # unsubscribe links are frequently longer
        lpart = parts[0]
        if len(lpart) > 128:
            return False

        # check if the domain is less than 255 octets
        domn = parts[1]
        if len(domn) > 253:
            return False

        # number of labels can not be over 127
        labels = domn.split('.')
        if len(labels) > 127:
            return False

        for label in labels:
            # check the domain doesn't start or end with - and
            # the length of each label is no more than 63 octets
            if BAD_DOMAIN.search(label) or len(label) > 63:
                return False

        return True

    def _address_list_relaxed(self):
        "Grammar: address-list-relaxed -> address { delimiter address }"
        #addrs = []
        addrs = flanker.addresslib.address.AddressList()
        unparsable = []

        # address
        addr = self._address()
        if addr is None:
            # synchronize to the next delimiter (or end of line)
            # append the skipped over text to the unparsable list
            skip = self.stream.synchronize()
            if skip:
                unparsable.append(skip)

            # if no mailbox and end of stream, we were unable
            # return the unparsable stream
            if self.stream.end_of_stream():
                return [], unparsable
        else:
            # if we found a delimiter or end of stream, we have a
            # valid mailbox, add it
            if self.stream.peek(DELIMITER) or self.stream.end_of_stream():
                addrs.append(addr)
            else:
                # otherwise snychornize and add it the unparsable array
                skip = self.stream.synchronize()
                if skip:
                    pre = self.stream.stream[:self.stream.stream.index(skip)]
                    unparsable.append(pre + skip)
                # if we hit the end of the stream, return the results
                if self.stream.end_of_stream():
                    return [], [self.stream.stream]

        while True:
            # delimiter
            dlm = self.stream.get_token(DELIMITER)
            if dlm is None:
                skip = self.stream.synchronize()
                if skip:
                    unparsable.append(skip)
                if self.stream.end_of_stream():
                    break

            # address
            start_pos = self.stream.position
            addr = self._address()
            if addr is None:
                skip = self.stream.synchronize()
                if skip:
                    unparsable.append(skip)

                if self.stream.end_of_stream():
                    break
            else:
                # if we found a delimiter or end of stream, we have a
                # valid mailbox, add it
                if self.stream.peek(DELIMITER) or self.stream.end_of_stream():
                    addrs.append(addr)
                else:
                    # otherwise snychornize and add it the unparsable array
                    skip = self.stream.synchronize()
                    if skip:
                        sskip = self.stream.stream[start_pos:self.stream.position]
                        unparsable.append(sskip)
                    # if we hit the end of the stream, return the results
                    if self.stream.end_of_stream():
                        return addrs, unparsable

        return addrs, unparsable

    def _address_list_strict(self):
        "Grammar: address-list-strict -> address { delimiter address }"
        #addrs = []
        addrs = flanker.addresslib.address.AddressList()

        # address
        addr = self._address()
        if addr is None:
            return addrs
        if self.stream.peek(DELIMITER):
            addrs.append(addr)

        while True:
            # delimiter
            dlm = self.stream.get_token(DELIMITER)
            if dlm is None:
                break

            # address
            addr = self._address()
            if addr is None:
                break
            addrs.append(addr)

        return addrs

    def _address(self):
        "Grammar: address -> name-addr-rfc | name-addr-lax | addr-spec | url"
        start_pos = self.stream.position

        addr = self._name_addr_rfc() or self._name_addr_lax() or \
            self._addr_spec() or self._url()

        # if email address, check that it passes post processing checks
        if addr and isinstance(addr, flanker.addresslib.address.EmailAddress):
            if self._mailbox_post_processing_checks(addr.address) is False:
                # roll back
                self.stream.position = start_pos
                return None

        return addr

    def _url(self):
        "Grammar: url -> url"
        earl = self.stream.get_token(URL)
        if earl is None:
            return None
        return flanker.addresslib.address.UrlAddress(to_utf8(earl))

    def _name_addr_rfc(self):
        "Grammar: name-addr-rfc -> [ display-name-rfc ] angle-addr-rfc"
        start_pos = self.stream.position

        # optional displayname
        dname = self._display_name_rfc()

        aaddr = self._angle_addr_rfc()
        if aaddr is None:
            # roll back
            self.stream.position = start_pos
            return None

        if dname:
            return flanker.addresslib.address.EmailAddress(dname, aaddr)
        return flanker.addresslib.address.EmailAddress(None, aaddr)

    def _display_name_rfc(self):
        "Grammar: display-name-rfc -> [ whitespace ] word { whitespace word }"
        wrds = []

        # optional whitespace
        self._whitespace()

        # word
        wrd = self._word()
        if wrd is None:
            return None
        wrds.append(wrd)

        while True:
            # whitespace
            wtsp = self._whitespace()
            if wtsp is None:
                break
            wrds.append(wtsp)

            # word
            wrd = self._word()
            if wrd is None:
                break
            wrds.append(wrd)

        return cleanup_display_name(''.join(wrds))

    def _angle_addr_rfc(self):
        '''
        Grammar: angle-addr-rfc -> [ whitespace ] < addr-spec > [ whitespace ]"
        '''
        start_pos = self.stream.position

        # optional whitespace
        self._whitespace()

        # left angle bracket
        lbr = self.stream.get_token(LBRACKET)
        if lbr is None:
            # rollback
            self.stream.position = start_pos
            return None

        # addr-spec
        aspec = self._addr_spec(True)
        if aspec is None:
            # rollback
            self.stream.position = start_pos
            return None

        # right angle bracket
        rbr = self.stream.get_token(RBRACKET)
        if rbr is None:
            # rollback
            self.stream.position = start_pos
            return None

         # optional whitespace
        self._whitespace()

        return aspec

    def _name_addr_lax(self):
        "Grammar: name-addr-lax -> [ display-name-lax ] angle-addr-lax"
        start_pos = self.stream.position

        # optional displayname
        dname = self._display_name_lax()

        aaddr = self._angle_addr_lax()
        if aaddr is None:
            # roll back
            self.stream.position = start_pos
            return None

        if dname:
            return flanker.addresslib.address.EmailAddress(dname, aaddr)
        return flanker.addresslib.address.EmailAddress(None, aaddr)

    def _display_name_lax(self):
        '''
        Grammar: display-name-lax ->
            [ whitespace ] word { whitespace word } whitespace"
        '''

        start_pos = self.stream.position
        wrds = []

        # optional whitespace
        self._whitespace()

        # word
        wrd = self._word()
        if wrd is None:
            # roll back
            self.stream.position = start_pos
            return None
        wrds.append(wrd)

        # peek to see if we have a whitespace,
        # if we don't, we have a invalid display-name
        if self.stream.peek(WHITESPACE) is None or \
            self.stream.peek(UNI_WHITE) is None:
            self.stream.position = start_pos
            return None

        while True:
            # whitespace
            wtsp = self._whitespace()
            if wtsp:
                wrds.append(wtsp)

            # if we need to roll back the next word
            start_pos = self.stream.position

            # word
            wrd = self._word()
            if wrd is None:
                self.stream.position = start_pos
                break
            wrds.append(wrd)

            # peek to see if we have a whitespace
            # if we don't pop off the last word break
            if self.stream.peek(WHITESPACE) is None or \
                self.stream.peek(UNI_WHITE) is None:
                # roll back last word
                self.stream.position = start_pos
                wrds.pop()
                break

        return cleanup_display_name(''.join(wrds))

    def _angle_addr_lax(self):
        "Grammar: angle-addr-lax -> addr-spec [ whitespace ]"
        start_pos = self.stream.position

        # addr-spec
        aspec = self._addr_spec(True)
        if aspec is None:
            # rollback
            self.stream.position = start_pos
            return None

        # optional whitespace
        self._whitespace()

        return aspec

    def _addr_spec(self, as_string=False):
        '''
        Grammar: addr-spec -> [ whitespace ] local-part @ domain [ whitespace ]
        '''
        start_pos = self.stream.position

        # optional whitespace
        self._whitespace()

        lpart = self._local_part()
        if lpart is None:
            # rollback
            self.stream.position = start_pos
            return None

        asym = self.stream.get_token(AT_SYMBOL)
        if asym is None:
            # rollback
            self.stream.position = start_pos
            return None

        domn = self._domain()
        if domn is None:
            # rollback
            self.stream.position = start_pos
            return None

        # optional whitespace
        self._whitespace()

        aspec = cleanup_email(''.join([lpart, asym, domn]))
        if as_string:
            return aspec
        return flanker.addresslib.address.EmailAddress(None, aspec)

    def _local_part(self):
        "Grammar: local-part -> dot-atom | quoted-string"
        return self.stream.get_token(DOT_ATOM) or \
            self.stream.get_token(QSTRING)

    def _domain(self):
        "Grammar: domain -> dot-atom"
        return self.stream.get_token(DOT_ATOM)

    def _word(self):
        "Grammar: word -> word-ascii | word-unicode"
        start_pos = self.stream.position

        # ascii word
        ascii_wrd = self._word_ascii()
        if ascii_wrd and not self.stream.peek(UNI_ATOM):
            return ascii_wrd

        # didn't get an ascii word, rollback to try again
        self.stream.position = start_pos

        # unicode word
        return self._word_unicode()

    def _word_ascii(self):
        "Grammar: word-ascii -> atom | qstring"
        return self.stream.get_token(ATOM) or self.stream.get_token(QSTRING)

    def _word_unicode(self):
        "Grammar: word-unicode -> unicode-atom | unicode-qstring"
        start_pos = self.stream.position

        # unicode atom
        uwrd = self.stream.get_token(UNI_ATOM)
        if uwrd and isinstance(uwrd, unicode) and \
            not contains_control_chars(uwrd) and not is_pure_ascii(uwrd):
            return uwrd

        # unicode qstr
        uwrd = self.stream.get_token(UNI_QSTR, 'qstr')
        if uwrd and isinstance(uwrd, unicode) and \
            not contains_control_chars(uwrd) and not is_pure_ascii(uwrd):
            return u'"{}"'.format(encode_string(None, uwrd))

        # rollback
        self.stream.position = start_pos
        return None


    def _whitespace(self):
        "Grammar: whitespace -> whitespace-ascii | whitespace-unicode"
        return self._whitespace_ascii() or self._whitespace_unicode()

    def _whitespace_ascii(self):
        "Grammar: whitespace-ascii -> whitespace-ascii"
        return self.stream.get_token(WHITESPACE)

    def _whitespace_unicode(self):
        "Grammar: whitespace-unicode -> whitespace-unicode"
        uwhite = self.stream.get_token(UNI_WHITE)
        if uwhite and not is_pure_ascii(uwhite):
            return uwhite
        return None


class ParserException(Exception):
    '''
    Exception raised when the parser encounters some parsing exception.
    '''
    def __init__(self, reason='Unknown parser error.'):
        self.reason = reason

    def __str__(self):
        return self.reason



MAX_ADDRESS_LENGTH = 512
MAX_ADDRESS_NUMBER = 1024
MAX_ADDRESS_LIST_LENGTH = MAX_ADDRESS_LENGTH * MAX_ADDRESS_NUMBER
