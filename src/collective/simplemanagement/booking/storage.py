#-*- coding: utf-8 -*-

import uuid

from persistent import Persistent
from BTrees.LOBTree import LOBTree

from zope.interface import implementer

from .content import Booking
from ..interfaces import IBooking
from ..interfaces import IBookingStorage


@implementer(IBookingStorage)
class BookingStorage(Persistent):

    def __init__(self):
        self.bookings = LOBTree()

    def __len__(self):
        """Returns the number of bookings.
        """
        return len(self.bookings)

    def __contains__(self, uuid):
        return uuid in self.bookings

    def __getitem__(self, uuid):
        return self.bookings[uuid]

    def add(self, booking):
        assert IBooking.providedBy(booking)
        self.bookings[booking.uuid] = booking

    def delete(self, uuid):
        del self.bookings[uuid]

    def create(self, **values):
        # TODO: check for required fields
        values['uuid'] = self._generate_uuid()
        booking = Booking(**values)
        self.add(booking)

    def _generate_uid(self):
        return uuid.uuid1().int

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

    def vocabulary(self, name):
        """Returns the list of values for the given index.
        """
