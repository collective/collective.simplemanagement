from datetime import datetime
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from zope.component import adapter
from zope.annotation import factory

from .interfaces import ITimeline
from .utils import datetimerange


AUTO_INDEX_PREFIX = 'index_'


def timeline(*ifaces):
    """A decorator that sets some useful variables at class definition time
    (``all_indexes``) and also sets up the adapter attributes,
    along with calling the whole annotation factory thingamajig.
    """
    def _wrapper(cls):
        all_indexes = []
        for name in dir(cls):
            if name.startswith(AUTO_INDEX_PREFIX) and \
                    callable(getattr(cls, name)):
                all_indexes.append(name[len(AUTO_INDEX_PREFIX):])
        cls.all_indexes = tuple(all_indexes)
        return factory(adapter(*ifaces)(cls))
    return _wrapper


class BaseTimeline(Persistent):
    """The base ``ITimeline`` adapter.

    Allows to quickly set up adapters for your content.
    """
    implements(ITimeline)

    def __init__(self):
        self.data = OOBTree()

    def snapshot(self, indexes=None, insert=True):
        """Should return a dictionary which has a key
        for every item in ``indexes``,
        and whose values are the correct values for the index
        **at this moment** on the context (``__parent__``).
        """
        now = datetime.now()
        snapshot = {}
        if indexes is None:
            indexes = self.all_indexes
        for index in indexes:
            data = {
                'prefix': AUTO_INDEX_PREFIX,
                'index': index
            }
            indexer = getattr(self, '%(prefix)s%(index)s' % data, None)
            if indexer is None:
                raise KeyError(
                    ("No indexer for '%(index)s' "
                     "(maybe add a '%(prefix)s%(index)s' method to the "
                     "timeline adapter)") % data)
            snapshot[index] = indexer(self._get_value(index))
        if insert:
            for index, value in snapshot.items():
                index = self._get_index(index)
                index[now] = value
        return snapshot

    def _get_index(self, index):
        return self.data.setdefault(index, OOBTree())

    def _get_value(self, index, limit=None):
        index = self._get_index(index, OOBTree())
        if len(index) == 0:
            return None
        if limit is None:
            return index[index.maxKey()]
        return index[index.maxKey(limit)]

    def slice(self, from_, to, resolution, indexes=None):
        if indexes is None:
            indexes = self.all_indexes
        for step in datetimerange(from_, to, resolution):
            yield { i: self._get_value(i, step) for i in indexes }
