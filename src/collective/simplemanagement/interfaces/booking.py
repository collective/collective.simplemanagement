from zope import schema
from zope.interface import Interface

from .. import _


class IBooking(Interface):

    date = schema.Date(
        title=_(u"Date"),
        required=True
    )

    time = schema.Decimal(
        title=_(u"Hours"),
        required=True
    )

    owner = schema.ASCIILine(
        title=_(u"Owner ID"),
        required=True
    )

    references = schema.Dict(
        title=_(u"Related objects"),
        required=False,
        key_type=schema.ASCIILine(title="Object type"),
        value_type=schema.ASCIILine(title="Object ID")
    )


class IOrderedSet(Interface):

    def __len__(self):
        """Returns the number of elements.
        """

    def __iter__(self):
        """Iterates over the elements
        """

    def __or__(self, other):
        """Merges two ``IOrderedSets`` so that no duplicates are present.

        Ordering is recomputed summing scores.
        """


class IBookingStorage(Interface):
    """Contains all the bookings.

    All of them.
    """

    def __len__(self):
        """Returns the number of bookings.
        """

    def __contains__(self, uuid):
        """Checks whether there is a booking with the given ``uuid``.

        Returns ``True`` or ``False``
        """

    def __getitem__(self, uuid):
        """Retrieves the ``IBooking`` object with the given ``uuid``.

        Raises ``KeyError`` if there is no booking with the given ``uuid``
        """

    def add(self, booking):
        """Adds the given ``booking`` and returns the assigned UUID.

        The ``booking`` object must implement ``IBooking``.
        """

    def delete(self, uuid):
        """Deletes the booking with the given ``uuid``.

        Raises ``KeyError`` if there is no booking with the given ``uuid``
        """

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


