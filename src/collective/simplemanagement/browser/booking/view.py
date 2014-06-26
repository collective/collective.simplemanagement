#-*- coding: utf-8 -*-
from urllib import urlencode

from zope.interface import implementer
from zope.interface import Interface
from zope.component import getMultiAdapter
# from zope.publisher.interfaces import NotFound
from zope.security import checkPermission

import plone.api
from plone.memoize import view
from plone.z3cform.layout import wrap_form
from plone.app.layout.globals.context import ContextState
from plone.app.layout.viewlets import ViewletBase

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode

from ... import _
from ... import api
from ...booking.form import EditForm
from ..widgets import book_widget
from .traverse import IBookingContainer


class DocumentBylineViewlet(ViewletBase):

    index = ViewPageTemplateFile('templates/byline.pt')

    def creator(self):
        helpers = getMultiAdapter(
            (self.context, self.request),
            name="helpers"
        )
        return helpers.info()['creator']


class BookingContextState(ContextState):

    @view.memoize
    def actions(self, category=None, max=-1):
        if category == 'object':
            helpers = getMultiAdapter(
                (self.context, self.request),
                name="helpers"
            )
            actions = [
                {
                    'category': 'object',
                    'available': True,
                    'description': u'',
                    'icon': '',
                    'title': _(u'View'),
                    'url': helpers.view_url(),
                    'visible': True,
                    'allowed': True,
                    'link_target': None,
                    'id': 'view'
                }
            ]
            if helpers.can_edit():
                actions.append({
                    'category': 'object',
                    'available': True,
                    'description': u'',
                    'icon': '',
                    'title': _(u'Edit'),
                    'url': helpers.edit_url(),
                    'visible': True,
                    'allowed': True,
                    'link_target': None,
                    'id': 'edit'
                })
        elif category == 'object_buttons':
            return []
        else:
            actions = super(BookingContextState, self).actions(
                category=category,
                max=max)
        return actions


class View(BrowserView):
    """IBooking View"""

    @property
    def info(self):
        helpers = getMultiAdapter((self.context, self.request),
                                  name="helpers")
        return helpers.info()


class ListingView(BrowserView):
    """IBooking listing View"""

    def form_action(self):
        return self.context.absolute_url()

    def tags(self):
        tags = self.request.form.get('tags', [])
        result = []
        for tag in tags:
            result.append({
                'tag': tag,
                'clear_url': self.clear_url_for(tag, tags)
            })
        return result

    def clear_url_for(self, tag, tags):
        new = [ t for t in tags if t != tag ]
        rq  = {
            f: v for f, v in self.request.form.items() if f != 'tags'
        }
        rq['tags:list'] = new
        return self.form_action() + '?' +  urlencode(rq, doseq=True)

    def info_for(self, booking):
        booking = self.context.publishTraverse(self.request, booking.uid)
        helpers = getMultiAdapter(
            (booking, self.request),
            name="helpers"
        )
        return helpers.info(self.context.__parent__)

    def bookings(self):
        return self.context.bookings(tags=self.request.get('tags', []))


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

    def format_text(context=None):
        """ formatted text for booking
        """

    def info(context=None):
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

    def format_text(self, context=None):
        return safe_unicode(
            book_widget.format_text(self.context, context=context)
        )

    def info(self, context=None):
        context = plone.api.portal.get()
        user_details = api.users.get_user_details(context, self.context.owner)
        booking = {
            'url': self.view_url(),
            'edit_url': self.edit_url(),
            'text': safe_unicode(
                book_widget.format_text(self.context, context=context)
            ),
            'time': self.context.time,
            'date': context.toLocalizedTime(self.context.date.isoformat()),
            'date2': api.date.timeago(self.context.date),
            'creator': user_details,
            'can_edit': self.can_edit(),
            'project': api.booking.get_project(self.context),
            'story': api.booking.get_story(self.context),
        }
        return booking


