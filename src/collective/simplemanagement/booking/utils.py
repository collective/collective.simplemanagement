from datetime import date
from zope.interface import implements
from zope import component

from ..interfaces import IBookingStorage
from .storage import BookingStorage


# Setup handlers
def install_utility(context):
    """Installs the utility into the site
    """
    data_file = 'collective-simplemanagement-install.txt'
    if context.readDataFile(data_file) is None:
        return
    site = context.getSite()
    sm = site.getSiteManager()
    utility = sm.queryUtility(IBookingStorage)
    if utility is None:
        # register it only if not exists
        utility = BookingStorage()
        sm.registerUtility(utility, IBookingStorage)


def remove_utility(context):
    """Removes the registered booking holes utility
    """
    data_file = 'collective-simplemanagement-uninstall.txt'
    if context.readDataFile(data_file) is None:
        return
    site = context.getSite()
    sm = site.getSiteManager()
    sm.unregisterUtility(provided=IBookingStorage)
