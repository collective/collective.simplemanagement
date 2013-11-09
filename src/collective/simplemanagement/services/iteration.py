from zope.security import checkPermission

from ..interfaces import IStoriesListing
from .. import api
from . import base


class JSONService(base.JSONService):

    def _get_stories(self):
        adpt = IStoriesListing(self.context)()
        return adpt.stories, adpt.totals

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    @api.permissions.accesscontrol("View")
    def view(self):
        """Return iteration's properties in this format
        {
            "title",
            "description",
            "is_sortable",
            "totals": {
                "hours",
                "estimate",
                "difference",
                "time_status"
            },
            "stories": [
                {
                    "id",
                    "UID",
                    "title",
                    "description",
                    "url",
                    "text",
                    "status",
                    "can_edit",
                    "epic",
                    "can_review",
                    "estimate",
                    "resource_time",
                    "difference",
                    "time_status",
                    "assignees": [
                    ],
                    "actions": [
                    ],
                    "milestone": '',
                }
                ...
            ]
        }
        """
        stories, totals = self._get_stories()

        return {
            'title': self.context.title,
            'is_sortable': self.user_can_manage_project,
            'description': self.context.description,
            'stories': stories,
            'totals': totals
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
