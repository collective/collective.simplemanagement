# -*- coding: utf-8 -*-

from OFS.SimpleItem import SimpleItem

from ZPublisher.BaseRequest import DefaultPublishTraverse

from zope.interface import implementer
from zope.interface import Interface
from zope.component import getUtility
from zope.component import adapts
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IRequest

import plone.api
from plone.uuid.interfaces import IUUID

from Products.CMFPlone.interfaces import IPloneSiteRoot

from ... import _
from ... import api
from ...interfaces import IBookingStorage
from ...interfaces import IProject
from ...interfaces import IStory


@implementer(IPublishTraverse)
class BaseContainer(SimpleItem):

    __parent__ = None
    __name__ = None
    id = ''
    title = ''
    utility_interface = None

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    @property
    def utility(self):
        return getUtility(self.utility_interface)

    def get_object(self, id):
        raise NotImplementedError(_("you must provide a get_object method"))

    def publishTraverse(self, request, obj_id):
        if obj_id:
            obj = self.get_object(obj_id)
            if obj:
                obj.__name__ = str(obj_id)
                obj.__parent__ = self
                return obj.__of__(self)
            else:
                raise NotFound(self, obj_id, request)

    def absolute_url(self):
        return '{0}/{1}'.format(self.__parent__.absolute_url(),
                                self.id)


class IBookingContainer(Interface):
    """
    """


@implementer(IBookingContainer)
class BookingContainer(BaseContainer):

    id = 'bookings'
    title = _(u"Bookings")
    utility_interface = IBookingStorage
    references = ()

    @property
    def __ac_local_roles__(self):
        parent = self.__parent__
        if parent is None:
            parent = plone.api.portal.get()
        local_roles = {}
        if hasattr(parent, '__ac_local_roles__'):
            if callable(parent.__ac_local_roles__):
                local_roles = parent.__ac_local_roles__()
            else:
                local_roles = parent.__ac_local_roles__
        return local_roles

    def get_object(self, uid):
        return self.utility[uid]

    def bookings(self, **kw):
        return api.booking.get_bookings(references=self.references)


class SiteBookingTraverser(DefaultPublishTraverse):
    """Traversal adapter for bookings
    """
    adapts(IPloneSiteRoot, IRequest)
    references = ()

    def fallback(self, request, name):
        return super(SiteBookingTraverser, self).publishTraverse(request, name)

    def publishTraverse(self, request, name):
        if name == BookingContainer.id:
            container = BookingContainer()
            container.__name__ = BookingContainer.id
            container.__parent__ = self.context
            container.references = self.references
            container = container.__of__(self.context)
            return container
        return self.fallback(request, name)


class ProjectBookingTraverser(SiteBookingTraverser):
    """Traversal adapter for bookings on projects
    """
    adapts(IProject, IRequest)

    @property
    def references(self):
        return (IUUID(self.context), )


class StoryBookingTraverser(ProjectBookingTraverser):
    """Traversal adapter for bookings on projects
    """
    adapts(IStory, IRequest)
