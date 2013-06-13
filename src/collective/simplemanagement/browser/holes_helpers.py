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
                'you also must provide a "userid" for dropping only single user\'s holes'
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
            if self.request.get('do-it-really-really'):
                util.users = OOBTree()
            else:
                return '\n'.join([
                    'you must provide a "do-it-really-really" in order to flush all data REALLY!!',
                    '#############################################################################',
                    "WARNING! you are going to drop all booking holes for this portal!!!",
                    '#############################################################################',
                ])
        return result


class HolesMgmt(BrowserView):

    def holes(self):
        util = component.getUtility(IBookingHoles)
        for hole in util:
            # {'hours': Decimal('7.0'),
            # 'reason': 'undefined',
            # 'user_id': 'm.delmonte',
            # 'day': (datetime.date(2013, 5, 30),)}
            yield hole
