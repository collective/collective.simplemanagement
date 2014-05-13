from zope.interface import implements
from persistent import Persistent

from .interfaces.booking import IBookingHole
from .interfaces.booking import IBookingHoles


class BookingHole(Persistent):
    """BBB: Backward compatibility
    """

    implements(IBookingHole)


class BookingHoles(Persistent):
    """BBB: Backward compatibility
    """

    implements(IBookingHoles)
