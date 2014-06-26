#-*- coding: utf-8 -*-

from Acquisition import aq_inner
from zope.security import checkPermission
from zope.component import getMultiAdapter

from Products.Five.browser import BrowserView

from plone.z3cform import z2
from z3c.form.interfaces import IFormLayer

from ...booking import BookingForm
from ... import api


class View(BrowserView):

    booking_limit = 10

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

    def get_booking(self):
        bookings = api.booking.get_bookings(references=self.context.UID())
        bookings = bookings[:self.booking_limit]

        def get_info(booking):
            return getMultiAdapter((booking, self.request),
                                   name="helpers").info(self.context)
        return [ get_info(el) for el in bookings ]

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
