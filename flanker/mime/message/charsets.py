from flanker.mime.message.utils import to_unicode


def convert_to_unicode(charset, value):
    #in case of unicode we have nothing to do
    if isinstance(value, unicode):
        return value

    charset = _translate_charset(charset)
    return to_unicode(value, charset=charset)


def _translate_charset(charset):
    """Translates crappy charset into Python analogue (if supported).

    Otherwise returns unmodified.
    """
    # ev: (ticket #2819)
    if 'sjis' in charset.lower():
        return 'shift_jis'

    # cp874 looks to be an alias for windows-874
    if 'windows-874' == charset.lower():
        return 'cp874'

    if 'koi8-r' in charset.lower():
        return 'koi8_r'

    if 'gb2312' in charset.lower():
        return 'gb2312'

    if 'gb18030' in charset.lower():
        return 'gb18030'

    if 'utf-8' in charset.lower() or charset.lower() == 'x-unknown':
        return 'utf-8'

    return charset
