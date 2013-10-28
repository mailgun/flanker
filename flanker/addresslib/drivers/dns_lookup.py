import collections
import dnsq


class DNSLookup(collections.MutableMapping):

    def __init__(self):
        pass

    def __getitem__(self, key):
        try:
            return dnsq.mx_hosts_for(key)
        except:
            return []

    def __setitem__(self, key, value):
        raise InvalidOperation('Setting MX record not supported.')

    def __delitem__(self, key):
        raise InvalidOperation('Deleting MX record not supported.')

    def __iter__(self):
        raise InvalidOperation('Iterating over MX records not supported.')

    def __len__(self):
        raise InvalidOperation('Length of MX records not supported.')


class InvalidOperation(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason
