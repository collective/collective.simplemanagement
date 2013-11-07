from Acquisition import aq_inner
from zope.security import checkPermission

from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView

from plone.z3cform import z2
from z3c.form.interfaces import IFormLayer

from ..interfaces import IStory
from ..booking import BookingForm
from ..utils import get_epic_by_story
from ..utils import get_assignees_details
from ..utils import get_bookings
from ..utils import get_timings
from ..utils import get_user_details


class View(BrowserView):

    def user_can_booking(self):
        if self.request.get('nobook'):
            return False
        return checkPermission('simplemanagement.AddBooking', self.context)

    def get_epic(self):
        return get_epic_by_story(self.context)

    def timing(self):
        return get_timings(self.context)

    def get_assignees(self):
        return get_assignees_details(self.context)

    def booking_format(self, brain):
        obj = brain.getObject()
        description = brain.Description
        description = description and description.splitlines()
        user_details = get_user_details(self.context, brain.Creator)
        booking = {
            # we force to unicode since the macro rendering engine needs unicode
            'title': safe_unicode(brain.Title),
            'description': safe_unicode(description),
            'time': brain.time,
            'href': safe_unicode(brain.getURL()),
            'date': self.context.toLocalizedTime(brain.date.isoformat()),
            'related': obj.get_related(),
            'creator': safe_unicode(user_details)
        }
        return booking

    def get_booking(self):
        return [self.booking_format(el)
                for el in get_bookings(project=self.context)]

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
