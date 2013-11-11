import time
from BTrees.LOBTree import LOBTree
from OFS.SimpleItem import SimpleItem


class CompassTool(SimpleItem):

    # XXX: all time values here should be stored as UTC,
    # and converted back into the proper "local" timezone
    # (which might differ per request) upon extraction from the tool.
    # But Zope and Plone support for all this must be investigated.

    def __init__(self):
        self.data = LOBTree()

    def __getitem__(self, tstamp):
        tstamp = long(tstamp)
        return self.data[tstamp]

    def __contains__(self, tstamp):
        return long(tstamp) in self.data

    def __len__(self):
        return len(self.data.keys())

    def keys(self, start, step, descending=True):
        # WARNING: I'm totally relying on the output of keys() to be sorted,
        # which is the case, but I couldn't find any formal guarantee
        raw_keys = self.data.keys()
        slice_ = []
        if descending:
            if start == 0:
                slice_ = raw_keys[-(start+step):]
            else:
                slice_ = raw_keys[-(start+step):-(start)]
            slice_ = [ i for i in slice_ ]
            slice_.reverse()
        else:
            slice_ = raw_keys[start:start+step]
        return [ k for k in slice_ ]

    def max_key(self):
        try:
            return self.data.maxKey()
        except ValueError:
            return None

    def add(self, data):
        now = long(time.time())
        self.data[now] = data
        return now

    def remove(self, tstamp):
        tstamp = long(tstamp)
        if tstamp in self.data:
            del self.data[tstamp]
