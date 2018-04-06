import collections
import os
import redis


class RedisCache(collections.MutableMapping):
    """
    RedisCache has the same interface as a dict, but talks to a redis server.
    """

    def __init__(self, host=None, port=None, prefix='mxr:', ttl=604800):
        self.prefix = prefix
        self.ttl = ttl

        host = host or os.environ.get('REDIS_HOST', 'localhost')
        port = port or os.environ.get('REDIS_PORT', 6379)
        db = os.environ.get('REDIS_DB', 0)
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def __getitem__(self, key):
        try:
            return self.r.get(self.__keytransform__(key))
        except:
            return None

    def __setitem__(self, key, value):
        try:
            return self.r.setex(self.__keytransform__(key), self.ttl, value)
        except:
            return None

    def __delitem__(self, key):
        self.r.delete(self.__keytransform__(key))

    def __iter__(self):
        try:
            return self.__value_generator__(self.r.keys(self.prefix + '*'))
        except:
            return iter([])

    def __len__(self):
        try:
            return len(self.r.keys(self.__keytransform__('*')))
        except:
            return 0

    def __keytransform__(self, key):
        return ''.join([self.prefix, str(key)])

    def __value_generator__(self, keys):
        for key in keys:
            yield self.r.get(key)
