import codecs

import six

from flanker.mime.message.utils import to_unicode

_ALIASES = {
    'sjis': 'shift_jis',
    'windows-874': 'cp874',
    'koi8-r': 'koi8_r'
}


def convert_to_unicode(charset, value):
    if isinstance(value, six.text_type):
        return value

    charset = _ensure_charset(charset)
    value = to_unicode(value, charset)
    return value


def _ensure_charset(charset):
    charset = charset.lower()
    try:
        codecs.lookup(charset)
        return charset
    except LookupError:
        pass

    charset = _ALIASES.get(charset)
    if charset:
        return charset

    return 'utf-8'
