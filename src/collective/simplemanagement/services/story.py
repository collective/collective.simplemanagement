import plone.api
from Acquisition import aq_parent
from Products.CMFCore.WorkflowCore import WorkflowException

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from .. import api
from . import base


class JSONService(base.JSONService):

    @api.permissions.accesscontrol("View")
    def view(self):
        """Return iteration's properties in this format
        {
            "id": '',
            "UID": '',
            "title": '',
            "description": '',
            "url": '',
            "text": '',
            "status": '',
            "can_edit": '',
            "epic": '',
            "can_review": '',
            "estimate": '',
            "resource_time": '',
            "difference": '',
            "time_status": '',
            "assignees": [
            ],

            "actions": [
            ],
            "milestone": '',
        }
        """
        can_edit = self.context.user_can_edit()
        can_review = self.context.user_can_review()

        timings = api.booking.get_timings(self.context)

        story = {
            "id": self.context.getId(),
            "UID": IUUID(self.context),
            "title": self.context.title,
            "description": self.context.description,
            "url": self.context.absolute_url(),
            "text": self.context.get_text(),
            "status": self.context.get_review_state(),
            "can_edit": self.context.user_can_edit(),
            "can_review": self.context.user_can_review(),
            "epic": api.content.get_epic_by_story(self.context),

            "estimate": timings['estimate'],
            "resource_time": timings['resource_time'],
            "difference": timings['difference'],
            "time_status": timings['time_status'],

            "assignees": api.users.get_assignees_details(self.context),
            "milestone": self.context.get_milestone(),
            "actions": self.context.get_actions()
        }
        return story

    @api.permissions.accesscontrol("Modify Portal Content")
    def change_iteration(self):
        """Move the story to the requested iteration
        """
        destination = self.request.get('destination')
        error = None
        if not destination:
            error = "destination doesn't exist"

        try:
            destination = uuidToObject(destination)
            destination.manage_pasteObjects(
                aq_parent(self.context).manage_cutObjects(
                    self.context.getId()))
        except:
            error = "An error occurred"

        return {
            'action': 'drop',
            'error': error
        }
