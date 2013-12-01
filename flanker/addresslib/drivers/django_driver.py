"""Django Cache Driver"""

import collections
try:
    from django.core.cache import get_cache
except ImportError:
    pass

class DjangoCache(collections.MutableMapping):
    """Cache that uses the Django Cache Backend"""
    def __init__(self, cache='default', prefix='mxr:', ttl=604800):
        """Initalize the cache

        Arguments:

        * cache -- the name of the Django cache to use (if not the default
                   cache)
        * prefix -- the prefix to use when setting mx record keys (defaults to
                    'mxr:')
        * ttl -- the timeout for mx record caches in seconds (defaults to 1
                 week)
        """
        self.prefix = prefix
        self.ttl = ttl
        self.cache = get_cache(cache)

    def __getitem__(self, key):
        """Get an item from the cache"""
        return self.cache.get(self.__keytransform__(key))

    def __setitem__(self, key, value):
        """Set a cache item"""
        return self.cache.set(self.__keytransform__(key), value, self.ttl)

    def __delitem__(self, key):
        """Delete an item from the cache"""
        self.cache.delete(self.__keytransform__(key))

    def __keytransform__(self, key):
        """Generate the key name"""
        return ''.join([self.prefix, str(key)])

    def __value_generator__(self, keys):
        """Generator to pull multiple keys"""
        for key in keys:
            yield self.cache.get(key)

    def __iter__(self):
        """Cache Iterator (not available with Django Cache)"""
        return iter([])

    def __len__(self):
        """Cache Length (not available with Django Cache)"""
        return 0
