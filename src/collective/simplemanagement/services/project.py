import plone.api
from zope.security import checkPermission

from datetime import date
from .. import api
from ..interfaces import IStoriesListing
from . import base


class JSONService(base.JSONService):

    def _get_stories(self, iteration):
        adpt = IStoriesListing(iteration)()
        return adpt.stories

    def _get_iterations(self):
        pc = plone.api.portal.get_tool(name='portal_catalog')
        return pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Iteration',
            'sort_on': 'start',
            'sort_order': 'ascending'
        })

    def user_can_manage_project(self, item):
        return checkPermission(
            'simplemanagement.ManageProject', item
        )

    def _format_iteration(self, item):
        start = None
        if item.start:
            start = item.start.isoformat()

        end = None
        if item.end:
            end = item.end.isoformat()

        return {
            "title": item.title,
            "description": item.description,
            "url": item.absolute_url(),
            'status': 'TODO',
            "stories": self._get_stories(item),
            "is_sortable": self.user_can_manage_project(item),
            "start": start,
            "end": end,
            "warning_delta_percent": self._settings.warning_delta_percent
        }

    @api.permissions.accesscontrol("View")
    def view(self):
        iterations = []
        for brain in self._get_iterations():
            obj = brain.getObject()
            iterations.append(self._format_iteration(obj))

        return {
            "title": self.context.title,
            "description": self.context.description,
            "iterations": iterations
        }
