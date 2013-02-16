import datetime
import json
import logging
from decimal import Decimal

from zope import component

from Products.Five.browser import BrowserView
from ..bookingholes import BookingHole
from ..interfaces import IBookingHoles

logger = logging.getLogger('collective.simplemanagement')


class CreateHole(BrowserView):

    @property
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')

    def process(self):
        date = self.request['date']
        date = [int(x) for x in date.split('-')]
        time = self.request['time']
        reason = self.request['reason']
        member = self.portal_state.member()
        # create hole
        hole = BookingHole(
            datetime.date(*date),
            Decimal(time),
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
