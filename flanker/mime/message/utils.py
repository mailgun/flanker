from cStringIO import StringIO
from contextlib import closing
from email.generator import Generator

def python_message_to_string(msg):
    """Converts python message to string in a proper way"""
    with closing(StringIO()) as fp:
        g = Generator(fp, mangle_from_=False)
        g.flatten(msg, unixfrom=False)
        return fp.getvalue()
