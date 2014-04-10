#-*- coding: utf-8 -*-

import uuid

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
# from BTrees.IFBTree import IFBucket
# from BTrees.IFBTree import IFSet
from BTrees.IFBTree import weightedUnion
# from BTrees.IFBTree import weightedIntersection
from zope.interface import implementer
from zope.event import notify

from ..interfaces import IBooking
from ..interfaces import IBookingStorage
from .content import Booking
from .catalog import setup_catalog
from .catalog import prepare_query
from .catalog import is_keyword_index
from .events import BookingAddedEvent


def _get_next_uid():
    return uuid.uuid1().hex


@implementer(IBookingStorage)
class BookingStorage(Persistent):

    def __init__(self):
        self.bookings = OOBTree()
        # we need real randomness for object keys
        # but we cannot use the same uid for zope.catalog ids
        # because it does not support 128bit integers
        # (and we do not like to use zope.intid).
        # So, we use different keys for storage and catalog
        # and we store mapping between them here.
        self.mapping = IOBTree()
        self.catalog = setup_catalog()

    def __len__(self):
        """Returns the number of bookings.
        """
        return len(self.bookings)

    def __contains__(self, uid):
        return uid in self.bookings

    def __getitem__(self, uid):
        return self.bookings[uid]

    def add(self, booking):
        assert IBooking.providedBy(booking)
        if not booking.uid:
            # maybe we are not using `create` method
            booking.uid = self._get_next_uid()
            booking.cat_id = self._get_next_cat_id()

        self.bookings[booking.uid] = booking
        self.index(booking)
        notify(BookingAddedEvent(booking))
        return booking.uid

    def delete(self, uid):
        booking = self.bookings.pop(uid)
        self.unindex(booking)

    def create(self, **values):
        booking = Booking(**values)
        self.add(booking)
        return booking

    def _get_next_uid(self):
        return _get_next_uid()

    def _get_next_cat_id(self):
        # we know that this id may not be unique
        # but we can reindex bookings if needed
        try:
            return self.mapping.maxKey() + 1
        except ValueError:
            # no keys yet
            return 1

    def _catalog_id_to_object(self, cat_id):
        uid = self.mapping[cat_id]
        return self.bookings[uid]

    def index(self, booking):
        self.catalog.index_doc(booking.cat_id, booking)
        self.mapping[booking.cat_id] = booking.uid

    def unindex(self, booking):
        self.catalog.unindex_doc(booking.cat_id)
        self.mapping.pop(booking.cat_id)

    def reindex_catalog(self):
        self.mapping.clear()
        self.catalog.clear()
        for booking in self.bookings:
            booking.cat_id = self._get_next_cat_id()
            self.index(booking)

    def _merge(self, op, sets):
        assert len(sets) > 1
        weight, merged = op(sets[0], sets[1])
        for set_ in sets:
            weight, merged = op(merged, set_)
        return weight, merged

    def _query(self, query, start=0, limit=None):
        results = []
        query = prepare_query(self.catalog, query)

        multiple_query = []
        for key, value in query.iteritems():
            if is_keyword_index(self.catalog, key) and len(value) > 1:
                for v in value:
                    partial_query = query.copy()
                    partial_query[key] = v
                    partial_results = self.catalog.apply(partial_query)
                    multiple_query.append(partial_results)
        if multiple_query:
            results = self._merge(weightedUnion, multiple_query)[1]
        else:
            results = self.catalog.apply(query)
        return results

    def query(self, query=None, start=0, limit=None):
        """Searches for bookings.

        Returns an ordered set of ``IBooking`` objects, which match ``query``.
        ``query`` is a dictionary with the keys being field names
        or keys contained in ``references``,
        and the values either a specific value
        or a range in the form of a ``(to, from)`` tuple
        (with ``None`` being no limit).

        ``start`` and ``limit`` can be used to slice the result set.
        """
        if not query:
            # the catalog does not like empty query
            # and returns None :S
            return self.bookings.values()

        _results = self._query(query, start=start, limit=limit)

        get_id = lambda x: x  # results = IFSet([1, 2, 3, 4, 5, 6])
        if hasattr(_results, 'items'):
            # results = IFBucket([(10, 1.0), (11, 1.0), (12, 1.0)])
            _results = _results.items()
            get_id = lambda x: x[0]

        limit = limit or len(_results)
        results = [self._catalog_id_to_object(get_id(item))
                   for item in _results][start:limit]

        return results

    def vocabulary(self, name):
        """Returns the list of values for the given index.
        """
