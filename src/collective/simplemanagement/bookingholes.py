from datetime import date
from zope.interface import implements
from zope import component
from persistent import Persistent
from BTrees.OOBTree import OOBTree

from .interfaces import IBookingHole, IBookingHoles


def create_hole(day, hours, user_id, reason=""):
    hole = BookingHole(day, hours, user_id, reason)
    util = component.getUtility(IBookingHoles)
    util.add(hole)
    return hole


class BookingHole(Persistent):

    implements(IBookingHole)

    def __init__(self, day, hours, user_id, reason):
        self.day = day
        self.hours = hours
        self.user_id = user_id
        self.reason = reason


class BookingHoles(Persistent):

    implements(IBookingHoles)

    def __init__(self):
        self.users = OOBTree()

    def add(self, hole):
        assert IBookingHole.providedBy(hole)
        user_holes = self.users.setdefault(hole.user_id, OOBTree())
        user_holes[hole.day] = hole

    def remove(self, user_id, day=None):
        if day is None:
            del self.users[user_id]
        else:
            del self.users[user_id][day]

    def iter_user(self, user_id, from_, to):
        assert isinstance(from_, date)
        assert isinstance(to, date)
        # if isinstance(from_, datetime):
        #     from_ = from_.date()

        # if isinstance(to, datetime):
        #     to = to.date()

        user_holes = self.users.get(user_id, None)
        if user_holes is not None:
            for key in user_holes.keys(min=from_, max=to):
                yield user_holes[key]

    def __contains__(self, user_id):
        return user_id in self.users

    def __iter__(self):
        for user_id in self.users.keys():
            for day in self.users[user_id].keys():
                yield self.users[user_id][day]

    def __len__(self):
        return len([h for h in self])


# Migration helper
def migrate_utility(context, migrate_hole):
    """Migrates the existing booking holes utility.

    ``migrate_hole`` must be a callable accepting two arguments:
    ``context``, which is the current ``context``,
    and ``hole``, which is the hole to be migrated.

    Must return a new, migrated hole object.
    """
    site = context.getSite()
    sm = site.getSiteManager()
    utility = sm.queryUtility(IBookingHoles)
    new_utility = BookingHoles()
    if utility is not None:
        for hole in utility:
            hole = migrate_hole(context, hole)
            new_utility.add(hole)
        sm.unregisterUtility(provided=IBookingHoles)
    sm.registerUtility(new_utility, IBookingHoles)


# Setup handlers
def install_utility(context):
    """Installs the utility into the site
    """
    data_file = 'collective-simplemanagement-install.txt'
    if context.readDataFile(data_file) is None:
        return
    site = context.getSite()
    sm = site.getSiteManager()
    utility = sm.queryUtility(IBookingHoles)
    if utility is None:
        utility = BookingHoles()
        sm.registerUtility(utility, IBookingHoles)


def remove_utility(context):
    """Removes the registered booking holes utility
    """
    data_file = 'collective-simplemanagement-bookingholes-uninstall.txt'
    if context.readDataFile(data_file) is None:
        return
    site = context.getSite()
    sm = site.getSiteManager()
    sm.unregisterUtility(provided=IBookingHoles)
