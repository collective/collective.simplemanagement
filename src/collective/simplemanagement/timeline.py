from datetime import datetime
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from zope.component import adapter, queryAdapter, provideAdapter
from zope.annotation import factory, IAnnotations
from zope.lifecycleevent.interfaces import IObjectMovedEvent

from .interfaces import ITimeline
from .configure import TIMELINE_ANNOTATIONS_KEY
from . import api


def timeline(*ifaces):
    """A decorator that sets some useful variables at class definition time
    (``all_indexes``) and also sets up the adapter attributes,
    along with calling the whole annotation factory thingamajig.
    """
    def _wrapper(cls):
        adapter_ = factory(
            adapter(*ifaces)(cls),
            key=TIMELINE_ANNOTATIONS_KEY)
        provideAdapter(adapter_)
        return cls
    return _wrapper


class BaseTimeline(Persistent):
    """The base ``ITimeline`` adapter.

    Allows to quickly set up adapters for your content.
    """
    implements(ITimeline)

    def __init__(self):
        self.data = OOBTree()
        self.__parent__ = None
        self.__name__ = None

    def index(self, context, indexes, previous):
        """Returns a dictionary whose keys are the values in ``indexes``
        and the values the index values as of now.

        ``context`` is the adapter context.

        ``previous`` is a dictionary containing the last inserted
        values of the specified ``indexes``.
        """

    def snapshot(self, context, indexes=None, insert=True):
        """Should return a dictionary which has a key
        for every item in ``indexes``,
        and whose values are the correct values for the index
        **at this moment** on the ``context``.
        """
        now = datetime.now()
        previous = {}
        if indexes is None:
            indexes = self.indexes
        for index in indexes:
            previous[index] = self._get_value(index)
        snapshot_ = self.index(context, indexes, previous)
        if insert:
            for index, value in snapshot_.items():
                index = self._get_index(index)
                index[now] = value
        return snapshot_

    def _get_index(self, index):
        return self.data.setdefault(index, OOBTree())

    def _get_value(self, index, limit=None):
        index = self._get_index(index)
        if len(index) == 0:
            return None
        if limit is not None:
            keys = index.keys(max=limit, excludemax=True)
            if len(keys) > 0:
                max_key = keys[-1]
            else:
                return None
        else:
            max_key = index.maxKey()
        return index[max_key]

    def slice(self, from_, to, resolution, indexes=None):
        if indexes is None:
            indexes = self.indexes
        for current, next in api.date.datetimerange(from_, to, resolution):
            result = {}
            for index in indexes:
                try:
                    result[index] = self._get_value(index, next)
                except ValueError:
                    result[index] = None
            yield (current, result)


def snapshot(object_, **kwargs):
    timeline_ = ITimeline(object_)
    timeline_.snapshot(object_, **kwargs)


def subscriber(object_, event):
    if not IObjectMovedEvent.providedBy(event):
        snapshot(object_)


def clear_timeline(object_):
    """Clears the timeline (throws away all data) for ``object_``.

    Should be used by uninstall.
    """
    annotations = queryAdapter(object_, IAnnotations, default={})
    if TIMELINE_ANNOTATIONS_KEY in annotations:
        del annotations[TIMELINE_ANNOTATIONS_KEY]
