# coding:utf-8

'''
Utility functions and classes used by flanker.
'''

def to_utf8(str_or_unicode):
    '''
    Safely returns a UTF-8 version of a given string
    >>> utils.to_utf8(u'hi')
        'hi'
    '''

    if isinstance(str_or_unicode, unicode):
        return str_or_unicode.encode("utf-8", "ignore")
    return str(str_or_unicode)


def is_pure_ascii(value):
    '''
    Determines whether the given string is a pure ascii
    string
    >>> utils.is_pure_ascii(u"Cаша")
        False
    >>> utils.is_pure_ascii(u"Alice")
        True
    >>> utils.is_pure_ascii("Alice")
        True
    '''

    if value is None:
        return False
    if not isinstance(value, basestring):
        return False

    try:
        value.encode("ascii")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False
    return True


def cleanup_display_name(name):
    return name.strip(''';,'\r\n ''')


def cleanup_email(email):
    return email.strip("<>;, ")
