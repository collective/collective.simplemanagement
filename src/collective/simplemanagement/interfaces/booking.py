#-*- coding: utf-8 -*-

from zope import schema
from zope.interface import Interface

from .. import _


class IBooking(Interface):
    """ schema for booking object
    """

    cat_id = schema.Int(
        title=_(u"Catalog id"),
        required=True
    )

    uid = schema.ASCIILine(
        title=_(u"UID"),
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

    references = schema.List(
        title=_(u"Related objects"),
        required=False,
        value_type=schema.Tuple(
            title=u"Reference",
            value_type=schema.ASCIILine(title=u'Stuff')
        )
    )

    tags = schema.Set(
        title=_(u"Tags"),
        required=False,
        value_type=schema.TextLine(title=u"Tag")
    )

    def index_references():
        """ returns the value to be indexed for ``references`` field
        """


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

    def _get_next_uid():
        """Return next id for a new booking
        """

    def _get_next_cat_id():
        """Return next id for a new catalog doc
        """

    def _catalog_id_to_object(cat_id):
        """Return next booking object by catalog id
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

    def index(booking):
        """Indexes a booking object.
        """

    def unindex(booking):
        """Unindexes a booking object.
        """

    def reindex_catalog():
        """Flushes catalog values and reindexes all bookings.
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


class IBookingHoles(Interface):
    """BBB: backward compatibility.
    """


class IBookingHole(Interface):
    """BBB: backward compatibility.
    """

