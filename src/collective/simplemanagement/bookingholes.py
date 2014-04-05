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


# def remove_utility(context):
#     """Removes the registered booking holes utility
#     """
#     data_file = 'collective-simplemanagement-bookingholes-uninstall.txt'
#     if context.readDataFile(data_file) is None:
#         return
#     site = context.getSite()
#     sm = site.getSiteManager()
#     sm.unregisterUtility(provided=IBookingHoles)
