#-*- coding: utf-8 -*-

import uuid

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from zope.interface import implementer
from zope.event import notify

from ..interfaces import IBooking
from ..interfaces import IBookingStorage
from .content import Booking
from .catalog import setup_catalog
from .catalog import prepare_query
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
            catalog_id = self._get_next_cat_id()
            booking.cat_id = catalog_id

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

    def reindex(self):
        self.mapping.clear()
        self.catalog.clear()
        for booking in self.bookings:
            booking.cat_id = self._get_next_cat_id()
            self.index(booking)

    def unindex(self, booking):
        self.catalog.unindex_doc(booking.cat_id)
        self.mapping.pop(booking.cat_id)

    def query(self, query, start=0, limit=None):
        """Searches for bookings.

        Returns an ordered set of ``IBooking`` objects, which match ``query``.
        ``query`` is a dictionary with the keys being field names
        or keys contained in ``references``,
        and the values either a specific value
        or a range in the form of a ``(to, from)`` tuple
        (with ``None`` being no limit).

        ``start`` and ``limit`` can be used to slice the result set.
        """
        if not query.keys():
            # the catalog does not like empty query
            # and returns None :S
            return self.bookings
        query = prepare_query(self.catalog, query)
        _results = self.catalog.apply(query)

        if hasattr(_results, 'items'):
            _results = _results.items()

        results = [self._catalog_id_to_object(item[0])
                   for item in _results]

        return results

    def vocabulary(self, name):
        """Returns the list of values for the given index.
        """
