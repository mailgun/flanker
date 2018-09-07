# coding:utf-8

"""
TokenStream represents a stream of tokens that a parser will consume.
TokenStream can be used to consume tokens, peek ahead, and synchonize to a
delimiter token. The tokens that the token stream operates on are either
compiled regular expressions or strings.
"""

import re
import six


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
        if isinstance(token, six.string_types) and len(token) == 1:
            if self.peek() == token:
                self.position += 1
                return token
            return None

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
            match = token.match(self.stream, self.position)
            if match:
                return self.stream[match.start():match.end()]
            return None
