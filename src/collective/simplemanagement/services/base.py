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
        """Set the action of this view:
        * view
        * modify
        * list
        * add
        * delete
        * update
        """
        request['TraversalRequestNameStack'] = []
        if name not in SERVICES:
            raise NotFound(self, "Not found", self.request)
        self.action = name
        return self

    @api.permissions.accesscontrol("View")
    def view(self):
        """Return some properties from the context"""
        return {
            'title': self.context.title,
            'description': self.context.description
        }

    @api.permissions.accesscontrol("Modify Portal Content")
    def modify(self):
        """Change some properties of the context
        """
        raise NotImplementedError

    @api.permissions.accesscontrol("View")
    def list(self):
        """Return a list of objects, depends on the context"""
        raise NotImplementedError

    @api.permissions.accesscontrol("Manage Portal")
    def add(self):
        """Add one o more elements to the context"""
        raise NotImplementedError

    @api.permissions.accesscontrol("Delete")
    def delete(self):
        """Delete some objects from the context"""
        raise NotImplementedError

    @api.permissions.accesscontrol("Add portal content")
    def update(self):
        """Update some object on the context"""
        raise NotImplementedError

    @api.jsonutils.jsonmethod()
    def __call__(self):
        """Return a json based on self.action parameter
        action represent a method described in this view
        """
        action = getattr(self, self.action, None)
        if not action:
            return ''
        else:
            return action()
