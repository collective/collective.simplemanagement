from BTrees.OOBTree import OOBTree

from zope import component

from Products.Five.browser import BrowserView
from ..interfaces import IBookingHoles


class FlushHoles(BrowserView):
    """ reset holes utility
    TO BE USED ONLY FOR TESTING PURPOSES!
    """

    def __call__(self):
        if not self.request.get('do-it-really'):
            # just a guard for accidental calling
            return 'you must provide a "do-it-really" in order to flush!'
        util = component.getUtility(IBookingHoles)
        util.users = OOBTree()
        return 'BOOKING HOLES UTILITY FLUSHED'
