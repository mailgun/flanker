import chardet
import regex as re
from flanker.mime.message import errors

def convert_to_unicode(charset, value):
    #in case of unicode we have nothing to do
    if isinstance(value, unicode):
        return value

    charset = _translate_charset(charset)

    #try to decode string strictly
    try:
        return value.decode(charset, 'strict')
    except (UnicodeError, LookupError):
        try:
            #try guess encoding and decode strictly
            return guess_and_convert(value)
        except Exception:
            return value.decode(charset, 'ignore')


def guess_and_convert(data):
    charset = chardet.detect(data)
    if not charset['encoding']:
        raise errors.DecodingError("Failed to guess encoding for %s" %(data, ))
    try:
        return data.decode(charset["encoding"], 'strict')
    except Exception, e:
        raise errors.DecodingError(str(e))


def _translate_charset(charset):
    """Translates crappy charset into Python analogue (if supported).

    Otherwise returns unmodified.
    """
    # ev: (ticket #2819)
    if "sjis" in charset.lower():
        return 'shift_jis'

    # cp874 looks to be an alias for windows-874
    if "windows-874" == charset.lower():
        return "cp874"

    if 'koi8-r' in charset.lower():
        return 'koi8_r'

    if 'utf-8' in charset.lower() or charset.lower() == 'x-unknown':
        return 'utf-8'

    return charset


RE_7BIT = ''
def is_7bit_string():
    pass
