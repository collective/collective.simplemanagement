import datetime
import json
import logging
from decimal import Decimal
from BTrees.OOBTree import OOBTree

from zope import component

from Products.Five.browser import BrowserView
from ..bookingholes import BookingHole
from ..interfaces import IBookingHoles
from ..configure import Settings


logger = logging.getLogger('collective.simplemanagement')


class CreateHole(BrowserView):

    @property
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')

    def process(self):
        date = self.request['date']
        date = [int(x) for x in date.split('-')]
        time = int(self.request['time'])
        reason = self.request['reason']
        settings = Settings()
        missing_time = settings.man_day_hours - time
        member = self.portal_state.member()
        # create hole
        hole = BookingHole(
            datetime.date(*date),
            Decimal(missing_time),
            member.getId(),
            reason=reason
        )
        util = component.getUtility(IBookingHoles)
        util.add(hole)
        return {
            'success': True,
            'error': None
        }

    def __call__(self):
        try:
            result = self.process()
        except Exception, e: # pylint: disable=W0703
            logger.exception("An error occurred while creating the booking hole")
            result = {
                'success': False,
                'error': str(e)
            }
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)


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
