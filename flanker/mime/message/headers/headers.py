from paste.util.multidict import MultiDict
from flanker.mime.message.headers.parsing import normalize, parse_stream
from flanker.mime.message.headers.encoding import to_mime
from flanker.mime.message.errors import EncodingError


class MimeHeaders(object):
    """Dictionary-like object that preserves the order and
    supports multiple values for the same key, knows
    whether it has been changed after the creation
    """

    def __init__(self, items=()):
        self.v = MultiDict(
            [(normalize(key), val) for (key, val) in items])
        self.changed = False

    def __getitem__(self, key):
        return self.v.get(normalize(key), None)

    def __len__(self):
        return len(self.v)

    def __iter__(self):
        return iter(self.v)

    def __contains__(self, key):
        return normalize(key) in self.v

    def __setitem__(self, key, value):
        self.v[normalize(key)] = _remove_newlines(value)
        self.changed = True

    def __delitem__(self, key):
        del self.v[normalize(key)]
        self.changed = True

    def __nonzero__(self):
        return len(self.v) > 0

    def prepend(self, key, val):
        self.v._items.insert(0, (key, _remove_newlines(val)))
        self.changed = True

    def add(self, key, value):
        """Adds header without changing the
        existing headers with same name"""

        self.v.add(normalize(key), _remove_newlines(value))
        self.changed = True

    def keys(self):
        """
        Returns the keys. (message header names)
        It remembers the order in which they were added, what
        is really important
        """
        return self.v.keys()

    def transform(self, fn):
        """Accepts a function, getting a key, val and returning
        a new pair of key, val and applies the function to all
        header, value pairs in the message.
        """

        changed = [False]
        def tracking_fn(key, val):
            new_key, new_val = fn(key, val)
            if new_val != val or new_key != key:
                changed[0] = True
            return new_key, new_val

        v = MultiDict(tracking_fn(key, val) for key, val in self.v.iteritems())
        if changed[0]:
            self.v = v
            self.changed = True


    def items(self):
        """
        Returns header,val pairs in the preserved order.
        """
        return list(self.iteritems())


    def iteritems(self):
        """
        Returns iterator header,val pairs in the preserved order.
        """
        return self.v.iteritems()


    def get(self, key, default=None):
        """
        Returns header value (case-insensitive).
        """
        return self.v.get(normalize(key), default)

    def getall(self, key):
        """
        Returns all header values by the given header name
        (case-insensitive)
        """
        return self.v.getall(normalize(key))

    def have_changed(self):
        """Tells whether someone has altered the headers
        after creation"""
        return self.changed

    def __str__(self):
        return str(self.v)

    @classmethod
    def from_stream(cls, stream):
        """Takes a stream and reads the headers,
        decodes headers to unicode dict like object"""
        return cls(parse_stream(stream))

    def to_stream(self, stream):
        """Takes a stream and serializes headers
        in a mime format"""

        for h, v in self.v.iteritems():
            try:
                h = h.encode('ascii')
            except UnicodeDecodeError:
                raise EncodingError("Non-ascii header name")
            stream.write("{}: {}\r\n".format(h, to_mime(h, v)))


def _remove_newlines(value):
    if not value:
        return ''
    elif isinstance(value, (str, unicode)):
        return value.replace('\r', '').replace('\n', '')
    else:
        return value
