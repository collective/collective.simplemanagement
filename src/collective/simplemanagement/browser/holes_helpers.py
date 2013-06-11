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
            return '\n'.join([
                'you must provide a "do-it-really" in order to flush!',
                'you can also pass a "userid" for dropping only single user\'s holes'
            ])
        result = 'BOOKING HOLES UTILITY FLUSHED'
        util = component.getUtility(IBookingHoles)
        if self.request.get('userid'):
            userid = self.request.get('userid')
            if userid in util:
                util.remove(userid)
                result += ' for user %s' % userid
            else:
                result = 'userid %s not found!' % userid
        else:
            util.users = OOBTree()
        return result
