from nose.tools import eq_

from flanker import _email


def test_encode_header_maxlinelen():
    """
    If the encoded string is longer then the maximum line length, which is 76,
    by default then it is broken down into lines. But a maximum line length
    value can be provided in the `maxlinelen` parameter.
    """
    eq_('very\r\n l' + ('o' * 70) + 'ng',
        _email.encode_header(None, 'very l' + ('o' * 70) + 'ng'))

    eq_('very l' + ('o' * 70) + 'ng',
        _email.encode_header(None, 'very l' + ('o' * 70) + 'ng',
                             max_line_len=78))
