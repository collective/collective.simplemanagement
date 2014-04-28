#-*- coding: utf-8 -*-

import plone.api

from zope.interface import implementer
from zope.interface import Interface
from zope.component import getMultiAdapter
# from zope.publisher.interfaces import IPublishTraverse
# from zope.publisher.interfaces import NotFound
# from zope.security import checkPermission

from plone.memoize import view

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from ... import api
from ..widgets import book_widget


class View(BrowserView):
    """IBooking View"""

    @property
    def info(self):
        helpers = getMultiAdapter((self.context, self.request),
                                  name="helpers")
        return helpers.info

# this view fails like this
#     2014-04-28 23:36:00 ERROR Zope.SiteErrorLog 1398720960.620.0422080793786 http://localhost:8180/simplemanagement/bookings/5acaa0f6cf1611e3854f0024d7c8e78c/edit
# Traceback (innermost last):
#   Module ZPublisher.Publish, line 134, in publish
#   Module Zope2.App.startup, line 301, in commit
#   Module transaction._manager, line 89, in commit
#   Module transaction._transaction, line 329, in commit
#   Module transaction._transaction, line 443, in _commitResources
#   Module ZODB.Connection, line 567, in commit
#   Module ZODB.Connection, line 623, in _commit
#   Module ZODB.Connection, line 658, in _store_objects
#   Module ZODB.serialize, line 422, in serialize
# TypeError: Can't pickle objects in acquisition wrappers.


class ListingView(BrowserView):
    """IBooking listing View"""

    def bookings(self):
        storage = api.booking.get_booking_storage()
        return storage.query()


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


@implementer(IHelpers)
class Helpers(BrowserView):

    def can_edit(self):
        # TODO
        return True

    @property
    @view.memoize_contextless
    def purl(self):
        portal = plone.api.portal.get()
        return portal.absolute_url()

    def view_url(self):
        return '{0}/bookings/{1}/view'.format(self.purl, self.context.uid)

    def edit_url(self):
        return '{0}/bookings/{1}/edit'.format(self.purl, self.context.uid)

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
            'creator': safe_unicode(user_details),
            'can_edit': self.can_edit(),
        }
        return booking
