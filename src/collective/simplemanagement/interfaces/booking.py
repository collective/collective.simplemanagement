#-*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from .. import _


class IBooking(Interface):
    """ schema for booking object
    """

    uuid = schema.Int(
        title=_(u"UUID"),
        required=True
    )

    date = schema.Date(
        title=_(u"Date"),
        required=True
    )

    time = schema.Decimal(
        title=_(u"Hours"),
        required=True
    )

    text = schema.TextLine(
        title=_(u"Text"),
        required=True
    )

    owner = schema.ASCIILine(
        title=_(u"Owner ID"),
        required=True
    )

    references = schema.Dict(
        title=_(u"Related objects"),
        required=False,
        key_type=schema.ASCIILine(title=u"Object type"),
        value_type=schema.ASCIILine(title=u"Object ID")
    )

    tags = schema.List(
        title=_(u"Tags"),
        required=False,
        value_type=schema.TextLine(title=u"Tag")
    )


class IBookingStorage(Interface):
    """Contains all the bookings.

    All of them.
    """

    def __len__():
        """Returns the number of bookings.
        """

    def __contains__(uuid):
        """Checks whether there is a booking with the given ``uuid``.

        Returns ``True`` or ``False``
        """

    def __getitem__(uuid):
        """Retrieves the ``IBooking`` object with the given ``uuid``.

        Raises ``KeyError`` if there is no booking with the given ``uuid``
        """

    def _generate_uuid():
        """Generates an UUID for the booking.
        This UUID is used both as storage key for the booking and indexing.
        """

    def add(booking):
        """Adds the given ``booking`` and returns the assigned UUID.

        The ``booking`` object must implement ``IBooking``.
        """

    def create(**values):
        """Given booking ``values`` it creates an ``ÌBooking`` object and
        it adds it to the storage. Returns the booking object.
        """

    def delete(uuid):
        """Deletes the booking with the given ``uuid``.

        Raises ``KeyError`` if there is no booking with the given ``uuid``
        """

    def query(query, start=0, limit=None):
        """Searches for bookings.

        Returns an ordered set of ``IBooking`` objects, which match ``query``.
        ``query`` is a dictionary with the keys being field names
        or keys contained in ``references``,
        and the values either a specific value
        or a range in the form of a ``(to, from)`` tuple
        (with ``None`` being no limit).

        ``start`` and ``limit`` can be used to slice the result set.
        """

    def vocabulary(name):
        """Returns the list of values for the given index.
        """
