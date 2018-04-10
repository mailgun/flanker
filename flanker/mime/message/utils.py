import chardet as fallback_detector
import six

# Made cchardet optional according to https://github.com/mailgun/flanker/pull/84
try:
    import cchardet as primary_detector
except ImportError:
    primary_detector = fallback_detector

from flanker.mime.message import errors


def _guess_and_convert_with(value, detector=primary_detector):
    """
    Try to guess the encoding of the passed value with the provided detector
    and decode it.

    The detector is either chardet or cchardet module.
    """
    charset = detector.detect(value)

    if not charset["encoding"]:
        raise errors.DecodingError("Failed to guess encoding")

    try:
        value = value.decode(charset["encoding"], "replace")
        return value

    except (UnicodeError, LookupError) as e:
        raise errors.DecodingError(str(e))


def _guess_and_convert(value):
    """
    Try to guess the encoding of the passed value and decode it.

    Uses cchardet to guess the encoding and if guessing or decoding fails, falls
    back to chardet which is much slower.
    """
    try:
        return _guess_and_convert_with(value, detector=primary_detector)
    except Exception:
        return _guess_and_convert_with(value, detector=fallback_detector)


def _make_unicode(value, charset=None):
    if isinstance(value, six.text_type):
        return value

    charset = charset or "utf-8"
    try:
        value = value.decode(charset, "strict")
    except (UnicodeError, LookupError):
        value = _guess_and_convert(value)

    return value


def to_utf8(value, charset=None):
    """
    Safely returns a UTF-8 version of a given string
    """
    value = _make_unicode(value, charset)

    return value.encode("utf-8", "strict")


def to_unicode(value, charset=None):
    return _make_unicode(value, charset)
