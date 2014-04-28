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

from Products.CMFPlone.interfaces import IPloneSiteRoot

from ... import _
from ...interfaces import IBookingStorage


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


class IBookingContainer(Interface):
    """
    """


@implementer(IBookingContainer)
class BookingContainer(BaseContainer):

    id = 'bookings'
    title = _(u"Bookings")
    utility_interface = IBookingStorage

    def get_object(self, uid):
        return self.utility[uid]


class BookingTraverser(DefaultPublishTraverse):
    """Traversal adapter for IUserFolder
    """
    adapts(IPloneSiteRoot, IRequest)

    def fallback(self, request, name):
        return super(BookingTraverser, self).publishTraverse(request, name)

    def publishTraverse(self, request, name):
        if name == BookingContainer.id:
            container = BookingContainer()
            container.__name__ = BookingContainer.id
            container.__parent__ = self.context
            container = container.__of__(self.context)
            return container
        return self.fallback(request, name)
