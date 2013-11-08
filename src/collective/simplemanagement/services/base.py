from zope.interface import implementer
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from .. import api
from ..interfaces import IJSONService


SERVICES = ('view', 'modify', 'list', 'add', 'delete', 'update')


@implementer(IJSONService, IPublishTraverse)
class JSONService(BrowserView):
    action = ''

    def publishTraverse(self, request, name):
        """Set view action"""
        request['TraversalRequestNameStack'] = []
        if name not in SERVICES:
            raise NotFound(self, "Not found", self.request)
        self.action = name
        return self

    @api.permissions.accesscontrol("View")
    def view(self):
        raise NotImplementedError

    @api.permissions.accesscontrol("Modify Portal Content")
    def modify(self):
        raise NotImplementedError

    @api.permissions.accesscontrol("View")
    def list(self):
        raise NotImplementedError

    @api.permissions.accesscontrol("Manage Portal")
    def add(self):
        raise NotImplementedError

    @api.permissions.accesscontrol("Delete")
    def delete(self):
        raise NotImplementedError

    @api.permissions.accesscontrol("Add portal content")
    def update(self):
        raise NotImplementedError

    def __call__(self):
        action = getattr(self, self.action, None)
        if not action:
            return ''
        else:
            return action()
