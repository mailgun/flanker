# coding:utf-8
"""
Tests for adjust_content_type() in flanker/mime/message/part.py.

These tests specifically cover the filetype-based image detection that
replaced the deprecated imghdr module.
"""
import pytest

from flanker.mime.message.part import adjust_content_type
from flanker.mime.message.headers import ContentType
from tests import MAILGUN_PNG


# Magic bytes for common image formats
JPEG_MAGIC = b'\xff\xd8\xff\xe0' + b'\x00' * 28
PNG_MAGIC = b'\x89PNG\r\n\x1a\n' + b'\x00' * 24
GIF_MAGIC = b'GIF89a' + b'\x00' * 26
BMP_MAGIC = b'BM' + b'\x00' * 30
# WebP requires: RIFF + size(4) + WEBP + VP8 chunk type(4)
WEBP_MAGIC = b'RIFF\x28\x00\x00\x00WEBPVP8 \x1c\x00\x00\x00' + b'\x00' * 16
# TIFF little-endian (II) and big-endian (MM)
TIFF_LE_MAGIC = b'II\x2a\x00' + b'\x00' * 28
TIFF_BE_MAGIC = b'MM\x00\x2a' + b'\x00' * 28


class TestAdjustContentTypeImageDetection:
    """Tests for filetype-based image subtype detection from body bytes."""

    def _image_ct(self, sub='octet-stream'):
        return ContentType('image', sub)

    def test_jpeg_detected_and_mapped(self):
        """filetype returns 'jpg', must be mapped to 'jpeg' for MIME."""
        ct = adjust_content_type(self._image_ct(), body=JPEG_MAGIC)
        assert str(ct) == 'image/jpeg'

    def test_png_detected(self):
        ct = adjust_content_type(self._image_ct(), body=PNG_MAGIC)
        assert str(ct) == 'image/png'

    def test_gif_detected(self):
        ct = adjust_content_type(self._image_ct(), body=GIF_MAGIC)
        assert str(ct) == 'image/gif'

    def test_bmp_detected(self):
        ct = adjust_content_type(self._image_ct(), body=BMP_MAGIC)
        assert str(ct) == 'image/bmp'

    def test_webp_detected(self):
        ct = adjust_content_type(self._image_ct(), body=WEBP_MAGIC)
        assert str(ct) == 'image/webp'

    def test_tiff_le_detected_and_mapped(self):
        """filetype returns 'tif', must be mapped to 'tiff' for MIME."""
        ct = adjust_content_type(self._image_ct(), body=TIFF_LE_MAGIC)
        assert str(ct) == 'image/tiff'

    def test_tiff_be_detected_and_mapped(self):
        ct = adjust_content_type(self._image_ct(), body=TIFF_BE_MAGIC)
        assert str(ct) == 'image/tiff'

    def test_unknown_body_keeps_original_subtype(self):
        """Non-image bytes: content type should not change."""
        ct = adjust_content_type(self._image_ct('jpeg'), body=b'notanimage' * 4)
        assert str(ct) == 'image/jpeg'

    def test_no_body_keeps_original_subtype(self):
        ct = adjust_content_type(self._image_ct('jpeg'), body=None)
        assert str(ct) == 'image/jpeg'

    def test_real_png_fixture(self):
        """Detection works on a real PNG binary (mailgun.png fixture)."""
        ct = adjust_content_type(self._image_ct('octet-stream'), body=MAILGUN_PNG)
        assert str(ct) == 'image/png'

    def test_only_preamble_used(self):
        """Detection is based on first 32 bytes; trailing garbage is ignored."""
        png_with_garbage = PNG_MAGIC + b'\xff' * 10000
        ct = adjust_content_type(self._image_ct(), body=png_with_garbage)
        assert str(ct) == 'image/png'

    def test_non_image_content_type_not_affected(self):
        """adjust_content_type should not touch non-image/non-audio content types."""
        ct = adjust_content_type(ContentType('text', 'plain'), body=PNG_MAGIC)
        assert str(ct) == 'text/plain'


class TestAdjustContentTypeFilename:
    """Tests for filename-based content type guessing (pre-existing behavior)."""

    def test_bz2_filename(self):
        ct = adjust_content_type(
            ContentType('application', 'octet-stream'), filename='archive.bz2')
        assert str(ct) == 'application/x-bzip2'

    def test_gz_filename(self):
        ct = adjust_content_type(
            ContentType('application', 'octet-stream'), filename='archive.gz')
        assert str(ct) == 'application/x-gzip'

    def test_png_filename(self):
        ct = adjust_content_type(
            ContentType('application', 'octet-stream'), filename='photo.png')
        assert str(ct) == 'image/png'

    def test_filename_ignored_when_not_octet_stream(self):
        """Filename guessing only triggers for application/octet-stream."""
        ct = adjust_content_type(
            ContentType('image', 'jpeg'), filename='photo.png')
        assert str(ct) == 'image/jpeg'
