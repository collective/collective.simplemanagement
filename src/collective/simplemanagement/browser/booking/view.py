from Products.Five.browser import BrowserView

import plone.api

from ... import api
from ..widgets import book_widget


class View(BrowserView):
    """IBooking View"""

    @property
    def booking_item(self):
        booking = None
        uid = self.request.get('uid')
        if uid:
            storage = api.booking.get_booking_storage()
            try:
                booking = storage[uid]
            except KeyError:
                booking = None
        return booking

    def bookings(self):
        # XXX: do not use me
        storage = api.booking.get_booking_storage()
        return storage.query()

    def render_text(self, booking):
        return book_widget.format_text(booking)

    def view_url(self, booking):
        return view_url(booking)


def view_url(booking, portal=None):
    if portal is None:
        portal = plone.api.portal.get()
    return portal.absolute_url() + '/@@booking?uid=' + str(booking.uid)
