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
    u'yahoo':       u'yahoo.com',
    u'gmail':       u'gmail.com',
    u'hotmail':     u'hotmail.com',
    u'live':        u'live.com',
    u'outlook':     u'outlook.com',
    u'msn':         u'msn.com',
    u'googlemail':  u'googlemail.com',
    u'aol':         u'aol.com',
    u'aim':         u'aim.com',
    u'icloud':      u'icloud.com',
    u'me':          u'me.com',
    u'mac':         u'mac.com',
    u'facebook':    u'facebook.com',
    u'comcast':     u'comcast.net',
    u'sbcglobal':   u'sbcglobal.net',
    u'bellsouth':   u'bellsouth.net',
    u'verizon':     u'verizon.net',
    u'earthlink':   u'earthlink.net',
    u'cox':         u'cox.net',
    u'charter':     u'charter.net',
    u'shaw':        u'shaw.ca',
    u'bell':        u'bell.net'
}
