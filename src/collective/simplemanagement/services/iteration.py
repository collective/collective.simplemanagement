from zope.security import checkPermission

from ..interfaces import IStoriesListing
from .. import api
from . import base


class JSONService(base.JSONService):

    def _get_stories(self):
        adpt = IStoriesListing(self.context)()
        return adpt.stories

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
            "start",
            "end",
            "warning_delta_percent",
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

        start = None
        if self.context.start:
            start = self.context.start.isoformat()

        end = None
        if self.context.end:
            end = self.context.end.isoformat()

        return {
            "title": self.context.title,
            "is_sortable": self.user_can_manage_project,
            "description": self.context.description,
            "stories": self._get_stories(),
            "start": start,
            "end": end,
            "warning_delta_percent": self._settings.warning_delta_percent
        }

    @api.permissions.accesscontrol("Manage Portal")
    def add(self, stories):
        """Add one o more stories to the context"""
        for data in stories:
            api.content.create_story(
                self.context, data, reindex=False
            )
