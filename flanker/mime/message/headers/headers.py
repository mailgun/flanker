from webob.multidict import MultiDict

from flanker.mime.message.headers import encodedword
from flanker.mime.message.headers.parsing import normalize, parse_stream
from flanker.mime.message.headers.encoding import to_mime
from flanker.mime.message.errors import EncodingError


class MimeHeaders(object):
    """Dictionary-like object that preserves the order and
    supports multiple values for the same key, knows
    whether it has been changed after the creation
    """

    def __init__(self, items=()):
        self._v = MultiDict([(normalize(key), remove_newlines(val))
                             for (key, val) in items])
        self.changed = False
        self.num_prepends = 0

    def __getitem__(self, key):
        v = self._v.get(normalize(key), None)
        if v is not None:
            return encodedword.decode(v)
        return None

    def __len__(self):
        return len(self._v)

    def __iter__(self):
        return iter(self._v)

    def __contains__(self, key):
        return normalize(key) in self._v

    def __setitem__(self, key, value):
        key = normalize(key)
        if key in self._v:
            self._v[key] = remove_newlines(value)
            self.changed = True
        else:
            self.prepend(key, remove_newlines(value))

    def __delitem__(self, key):
        del self._v[normalize(key)]
        self.changed = True

    def __nonzero__(self):
        return len(self._v) > 0

    def prepend(self, key, value):
        self._v._items.insert(0, (normalize(key), remove_newlines(value)))
        self.num_prepends += 1

    def add(self, key, value):
        """Adds header without changing the
        existing headers with same name"""
        self.prepend(key, value)

    def keys(self):
        """
        Returns the keys. (message header names)
        It remembers the order in which they were added, what
        is really important
        """
        return self._v.keys()

    def transform(self, fn, decode=False):
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

        v = MultiDict(tracking_fn(key, val) for key, val in self.iteritems(raw=not decode))
        if changed[0]:
            self._v = v
            self.changed = True

    def items(self):
        """
        Returns header,val pairs in the preserved order.
        """
        return list(self.iteritems())

    def iteritems(self, raw=False):
        """
        Returns iterator header,val pairs in the preserved order.
        """
        if raw:
            return self._v.iteritems()

        return iter([(x[0], encodedword.decode(x[1]))
                     for x in self._v.iteritems()])

    def get(self, key, default=None):
        """
        Returns header value (case-insensitive).
        """
        v = self._v.get(normalize(key), default)
        if v is not None:
            return encodedword.decode(v)
        return None

    def getraw(self, key, default=None):
        """
        Returns raw header value (case-insensitive, non-decoded.
        """
        return self._v.get(normalize(key), default)

    def getall(self, key):
        """
        Returns all header values by the given header name (case-insensitive).
        """
        v = self._v.getall(normalize(key))
        return [encodedword.decode(x) for x in v]

    def have_changed(self, ignore_prepends=False):
        """
        Tells whether someone has altered the headers after creation.
        """
        return self.changed or (self.num_prepends > 0 and not ignore_prepends)

    def __str__(self):
        return str(self._v)

    @classmethod
    def from_stream(cls, stream):
        """
        Takes a stream and reads the headers, decodes headers to unicode dict
        like object.
        """
        return cls(parse_stream(stream))

    def to_stream(self, stream, prepends_only=False):
        """
        Takes a stream and serializes headers in a mime format.
        """
        i = 0
        for h, v in self.iteritems(raw=True):
            if prepends_only and i == self.num_prepends:
                break
            i += 1
            try:
                h = h.encode('ascii')
            except UnicodeDecodeError:
                raise EncodingError("Non-ascii header name")
            stream.write("{0}: {1}\r\n".format(h, to_mime(h, v)))


def remove_newlines(value):
    if not value:
        return ''
    elif isinstance(value, (str, unicode)):
        return value.replace('\r', '').replace('\n', '')
    else:
        return value
