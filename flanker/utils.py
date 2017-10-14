# coding:utf-8
"""
Utility functions and classes used by flanker.
"""
import re
from functools import wraps

import six


def is_pure_ascii(value):
    """
    Determines whether the given string is a pure ascii
    string
    >>> utils.is_pure_ascii(u"Cаша")
        False
    >>> utils.is_pure_ascii(u"Alice")
        True
    >>> utils.is_pure_ascii("Alice")
        True
    """

    if value is None:
        return False

    if isinstance(value, six.binary_type):
        try:
            value.decode('ascii')
        except UnicodeDecodeError:
            return False

        return True

    if isinstance(value, six.text_type):
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            return False

        return True

    return False


def cleanup_display_name(name):
    return name.strip(''';,'\r\n ''')


def cleanup_email(email):
    return email.strip("<>;, ")


def contains_control_chars(s):
    if CONTROL_CHAR_RE.match(s):
        return True
    return False


def metrics_wrapper():

    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return_value = f(*args, **kwargs)
            if 'metrics' in kwargs and kwargs['metrics'] == True:
                #return all values
                return return_value

            # if we have a single item
            if len(return_value[:-1]) == 1:
                return return_value[0]

            # return all except the last value
            return return_value[:-1]

        return wrapper

    return decorate


# allows, \t\n\v\f\r (0x09-0x0d)
CONTROL_CHARS = ''.join([six.unichr(c) for c in range(0, 9)] +
                        [six.unichr(c) for c in range(14, 32)] +
                        [six.unichr(c) for c in range(127, 160)])
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(CONTROL_CHARS))
