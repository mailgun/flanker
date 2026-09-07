"""
Minimal image-type detection.

Replaces the use of the standard-library ``imghdr`` module, which was
deprecated in Python 3.11 and removed in Python 3.13. Only the ``what()``
entry point that flanker relies on is provided, with the same recogniser
set and return values as CPython's ``imghdr`` so that behaviour is
unchanged.
"""

__all__ = ["what"]


def _test_jpeg(h):
    if h[6:10] in (b'JFIF', b'Exif'):
        return 'jpeg'
    if h[:4] == b'\xff\xd8\xff\xdb':
        return 'jpeg'
    return None


def _test_png(h):
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    return None


def _test_gif(h):
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    return None


def _test_tiff(h):
    if h[:2] in (b'MM', b'II'):
        return 'tiff'
    return None


def _test_rgb(h):
    if h[:2] == b'\x01\xda':
        return 'rgb'
    return None


def _test_pbm(h):
    if len(h) >= 3 and h[0:1] == b'P' and h[1:2] in b'14' and h[2:3] in b' \t\n\r':
        return 'pbm'
    return None


def _test_pgm(h):
    if len(h) >= 3 and h[0:1] == b'P' and h[1:2] in b'25' and h[2:3] in b' \t\n\r':
        return 'pgm'
    return None


def _test_ppm(h):
    if len(h) >= 3 and h[0:1] == b'P' and h[1:2] in b'36' and h[2:3] in b' \t\n\r':
        return 'ppm'
    return None


def _test_bmp(h):
    if h[:2] == b'BM':
        return 'bmp'
    return None


def _test_webp(h):
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'
    return None


def _test_exr(h):
    if h[:4] == b'\x76\x2f\x31\x01':
        return 'exr'
    return None


_TESTS = (_test_jpeg, _test_png, _test_gif, _test_tiff, _test_rgb, _test_pbm,
          _test_pgm, _test_ppm, _test_bmp, _test_webp, _test_exr)


def what(file, h=None):
    """Return the image type of the given file/bytes, or None.

    Mirrors ``imghdr.what``: ``h`` may be passed directly as a bytes header,
    otherwise ``file`` is opened (path) or read (file-like object).
    """
    if h is None:
        if isinstance(file, (str, bytes)) and not hasattr(file, 'read'):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
    for test in _TESTS:
        result = test(h)
        if result:
            return result
    return None
