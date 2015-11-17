# coding:utf-8

"""
TokenStream represents a stream of tokens that a parser will consume.
TokenStream can be used to consume tokens, peek ahead, and synchonize to a
delimiter token. The tokens that the token stream operates on are either
compiled regular expressions or strings.
"""

import re
from flanker.addresslib import ASCII_FLAG


LBRACKET   = b'<'
AT_SYMBOL  = b'@'
RBRACKET   = b'>'
DQUOTE     = b'"'

BAD_DOMAIN = re.compile(r'''                                    # start or end
                        ^-|-$                                   # with -
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

DELIMITER  = re.compile(r'''
                        [,;][,;\s]*                             # delimiter
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

WHITESPACE = re.compile(r'''
                        (\ |\t)+                                # whitespace
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

UNI_WHITE  = re.compile(ur'''
                        [
                            \u0020\u00a0\u1680\u180e
                            \u2000-\u200a
                            \u2028\u202f\u205f\u3000
                        ]*
                        ''', re.MULTILINE | re.VERBOSE | re.UNICODE)

RELAX_ATOM = re.compile(r'''
                        ([^\s<>;,"]+)
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

ATOM       = re.compile(r'''
                        [A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+        # atext
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

DOT_ATOM   = re.compile(r'''
                        [A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+        # atext
                        (\.[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]+)*   # (dot atext)*
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

UNI_ATOM = re.compile(ur'''
                        ([^\s<>;,"]+)
                        ''', re.MULTILINE | re.VERBOSE | re.UNICODE)

UNI_QSTR   = re.compile(ur'''
                        "
                        (?P<qstr>([^"]+))
                        "
                        ''', re.MULTILINE | re.VERBOSE | re.UNICODE)

QSTRING    = re.compile(r'''
                        "                                       # dquote
                        (\s*                                    # whitespace
                        ([\x21\x23-\x5b\x5d-\x7e]               # qtext
                        |                                       # or
                        \\[\x21-\x7e\t\ ]))*                    # quoted-pair
                        \s*                                     # whitespace
                        "                                       # dquote
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

URL        = re.compile(r'''
                        (?:http|https)://
                        [^\s<>{}|\^~\[\]`;,]+
                        ''', re.MULTILINE | re.VERBOSE | ASCII_FLAG)

UNI_URL        = re.compile(ur'''
                        (?:http|https)://
                        [^\s<>{}|\^~\[\]`;,]+
                        ''', re.MULTILINE | re.VERBOSE | re.UNICODE)

class TokenStream(object):
    """
    Represents the stream of tokens that the parser will consume. The token
    stream can be used to consume tokens, peek ahead, and synchonize to a
    delimiter token.

    When the strem reaches its end, the position is placed
    at one plus the position of the last token.
    """
    def __init__(self, stream):
        self.position = 0
        self.stream = stream

    def get_token(self, token, ngroup=None):
        """
        Get the next token from the stream and advance the stream. Token can
        be either a compiled regex or a string.
        """
        # match single character
        if isinstance(token, str) and len(token) == 1:
            if isinstance(self.stream, unicode):
                token = token.decode('iso-8859-1')
            if self.peek() == token:
                self.position += 1
                return token
            return None

        if isinstance(token, unicode) and len(token) == 1:
            if isinstance(self.stream, str):
                token = token.encode('iso-8859-1')
            if self.peek() == token:
                self.position += 1
                return token
            return None

        # do not match a unicode pattern against bytes stream
        if isinstance(token.pattern, unicode) and isinstance(self.stream, str):
            return None

        # convert bytes pattern to unicode when matching against a unicode stream
        if isinstance(token.pattern, str) and isinstance(self.stream, unicode):
            token = re.compile(token.pattern.decode('iso-8859-1'), token.flags)

        # match a pattern
        match = token.match(self.stream, self.position)
        if match:
            advance = match.end() - match.start()
            self.position += advance

            # if we are asking for a named capture, return jus that
            if ngroup:
                return match.group(ngroup)
            # otherwise return the entire capture
            return match.group()

        return None

    def end_of_stream(self):
        """
        Check if the end of the stream has been reached, if it has, returns
        True, otherwise false.
        """
        if self.position >= len(self.stream):
            return True
        return False

    def synchronize(self):
        """
        Advances the stream to synchronizes to the delimiter token. Used primarily
        in relaxed mode parsing.
        """
        start_pos = self.position
        end_pos = len(self.stream)

        match = DELIMITER.search(self.stream, self.position)
        if match:
            self.position = match.start()
            end_pos = match.start()
        else:
            self.position = end_pos

        skip = self.stream[start_pos:end_pos]
        if skip.strip() == '':
            return None

        return skip

    def peek(self, token=None):
        """
        Peek at the stream to see what the next token is or peek for a
        specific token.
        """
        # peek at whats next in the stream
        if token is None:
            if self.position < len(self.stream):
                return self.stream[self.position]
            else:
                return None
        # peek for a specific token
        else:
            # do not match a unicode pattern against bytes stream
            if isinstance(token.pattern, unicode) and isinstance(self.stream, str):
                return None

            # convert bytes pattern to unicode when matching against a unicode stream
            if isinstance(token.pattern, str) and isinstance(self.stream, unicode):
                token = re.compile(token.pattern.decode('iso-8859-1'), token.flags)

            match = token.match(self.stream, self.position)
            if match:
                return self.stream[match.start():match.end()]
            return None
