#-*- coding: utf-8 -*-


from zope.interface import implementer
from zope.interface import Interface
from zope.component import getMultiAdapter
# from zope.publisher.interfaces import NotFound
from zope.security import checkPermission

import plone.api
from plone.memoize import view
from plone.z3cform.layout import wrap_form

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from ... import api
from ...booking.form import EditForm
from ..widgets import book_widget
from .traverse import IBookingContainer


class View(BrowserView):
    """IBooking View"""

    @property
    def info(self):
        helpers = getMultiAdapter((self.context, self.request),
                                  name="helpers")
        return helpers.info


class ListingView(BrowserView):
    """IBooking listing View"""

    def info_for(self, booking):
        helpers = getMultiAdapter(
            (booking, self.request),
            name="helpers"
        )
        return helpers.info


class IHelpers(Interface):

    def can_edit():
        """ check if user can edit
        """

    def view_url():
        """ return view url for viewing booking
        """

    def edit_url():
        """ return edit url for viewing booking
        """

    def format_text():
        """ formatted text for booking
        """

    def info():
        """ booking info for view rendering
        """

EditView = wrap_form(EditForm)


@implementer(IHelpers)
class Helpers(BrowserView):

    def can_edit(self):
        return checkPermission('simplemanagement.EditBooking', self.context)

    @property
    def parent_url(self):
        # this should be the /bookings traverser in the context
        # XXX: any better way to get this?
        parent = self.request.PARENTS[0]
        if IBookingContainer.providedBy(parent):
            return parent.absolute_url()
        portal = plone.api.portal.get()
        return portal.absolute_url() + '/bookings'

    @view.memoize
    def view_url(self):
        return '{0}/{1}/view'.format(self.parent_url,
                                     self.context.uid)

    @view.memoize
    def edit_url(self):
        return '{0}/{1}/edit'.format(self.parent_url,
                                     self.context.uid)

    def format_text(self):
        return safe_unicode(book_widget.format_text(self.context))

    @property
    def info(self):
        context = plone.api.portal.get()
        user_details = api.users.get_user_details(context, self.context.owner)
        booking = {
            'url': self.view_url(),
            'edit_url': self.edit_url(),
            'text': safe_unicode(book_widget.format_text(self.context)),
            'time': self.context.time,
            'date': context.toLocalizedTime(self.context.date.isoformat()),
            'date2': api.date.timeago(self.context.date),
            'creator': user_details,
            'can_edit': self.can_edit(),
            'project': api.booking.get_project(self.context),
            'story': api.booking.get_story(self.context),
        }
        return booking


