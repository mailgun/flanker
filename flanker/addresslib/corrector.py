# coding:utf-8
"""
Spelling corrector library, used to correct common typos in domains like
gmal.com instead of gmail.com.

The spelling corrector uses difflib which in turn uses the
Ratcliff-Obershelp algorithm [1] to compute the similarity of two strings.
This is a very fast an accurate algorithm for domain spelling correction.

The (only) public method this module has is suggest(word), which given
a domain, suggests an alternative or returns the original domain
if no suggestion exists.

[1] http://xlinux.nist.gov/dads/HTML/ratcliffObershelp.html
"""

import difflib


def suggest(word, cutoff=0.77):
    """
    Given a domain and a cutoff heuristic, suggest an alternative or return the
    original domain if no suggestion exists.
    """
    if word in LOOKUP_TABLE:
        return LOOKUP_TABLE[word]

    guess = difflib.get_close_matches(word, MOST_COMMON_DOMAINS, n=1, cutoff=cutoff)
    if guess and len(guess) > 0:
        return guess[0]
    return word


MOST_COMMON_DOMAINS = [
    # mailgun :)
    b'mailgun.net',
    # big esps
    b'yahoo.com',
    b'yahoo.ca',
    b'yahoo.co.jp',
    b'yahoo.co.uk',
    b'yahoo.com.br',
    b'ymail.com',
    b'hotmail.com',
    b'hotmail.ca',
    b'hotmail.co.uk',
    b'windowslive.com',
    b'live.com',
    b'outlook.com',
    b'msn.com',
    b'gmail.com',
    b'googlemail.com',
    b'aol.com',
    b'aim.com',
    b'icloud.com',
    b'me.com',
    b'mac.com',
    b'facebook.com',
    # big isps
    b'comcast.net',
    b'sbcglobal.net',
    b'bellsouth.net',
    b'verizon.net',
    b'earthlink.net',
    b'cox.net',
    b'charter.net',
    b'shaw.ca',
    b'bell.net'
]

# domains that the corrector doesn't fix that we should fix
LOOKUP_TABLE = {
    b'yahoo':       b'yahoo.com',
    b'gmail':       b'gmail.com',
    b'hotmail':     b'hotmail.com',
    b'live':        b'live.com',
    b'outlook':     b'outlook.com',
    b'msn':         b'msn.com',
    b'googlemail':  b'googlemail.com',
    b'aol':         b'aol.com',
    b'aim':         b'aim.com',
    b'icloud':      b'icloud.com',
    b'me':          b'me.com',
    b'mac':         b'mac.com',
    b'facebook':    b'facebook.com',
    b'comcast':     b'comcast.net',
    b'sbcglobal':   b'sbcglobal.net',
    b'bellsouth':   b'bellsouth.net',
    b'verizon':     b'verizon.net',
    b'earthlink':   b'earthlink.net',
    b'cox':         b'cox.net',
    b'charter':     b'charter.net',
    b'shaw':        b'shaw.ca',
    b'bell':        b'bell.net'
}
