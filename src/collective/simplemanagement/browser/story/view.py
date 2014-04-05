from Acquisition import aq_inner
from zope.security import checkPermission

from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView

from plone.z3cform import z2
from z3c.form.interfaces import IFormLayer

from ...booking import BookingForm
from ... import api
from ..widgets import book_widget
from ..booking.view import view_url


class View(BrowserView):

    def user_can_booking(self):
        if self.request.get('nobook'):
            return False
        return checkPermission('simplemanagement.AddBooking', self.context)

    def get_epic(self):
        return api.content.get_epic_by_story(self.context)

    def timing(self):
        return api.booking.get_timings(self.context)

    def get_assignees(self):
        return api.users.get_assignees_details(self.context)

    def booking_format(self, booking):
        user_details = api.users.get_user_details(self.context, booking.owner)
        booking = {
            # we force to unicode since the macro rendering
            # engine needs unicode
            # TODO: booking transform text
            'url': view_url(booking),
            'text': safe_unicode(book_widget.format_text(booking.text)),
            'time': booking.time,
            'date': self.context.toLocalizedTime(booking.date.isoformat()),
            'creator': safe_unicode(user_details)
        }
        return booking

    def get_booking(self):
        get_bookings = api.booking.get_bookings
        return [self.booking_format(el)
                for el in get_bookings(references=self.context.UID())]

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
