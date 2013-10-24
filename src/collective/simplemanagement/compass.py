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

    def keys(self, descending=True, min=None, max=None,
             excludemin=False, excludemax=False, limit=None):
        raw_keys = self.data.keys(
            max=max,
            min=min,
            excludemin=excludemin,
            excludemax=excludemax
        )
        if descending:
            iter_ = xrange(-1, -1*(min(limit, len(raw_keys))+1), -1)
        else:
            iter_ = xrange(0, min(limit, len(raw_keys)))
        return [ raw_keys[i] for i in iter_ ]

    def add(self, data):
        now = long(time.time())
        self.data[now] = data
