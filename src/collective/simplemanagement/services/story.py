import plone.api
from Acquisition import aq_parent
from Products.CMFCore.WorkflowCore import WorkflowException

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from .. import api
from . import base

from .. import messageFactory as _


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

            "assignees": api.users.get_assignees_details(self.context),
            "milestone": self.context.get_milestone(),
            "actions": self.context.get_actions(),
            'warning_delta_percent': self._settings.warning_delta_percent
        }
        return story

    @api.permissions.accesscontrol("Modify Portal Content")
    def change_iteration(self):
        """Move the story to the requested iteration
        """
        destination_uid = self.request.get('destination')
        destination = uuidToObject(destination_uid)

        if not destination:
            error = True
            message = _(u"Iteration destination doesn't exist")

        error = False
        message = _(
            u"${story} moved to ${iteration}",
            mapping={
                "story": self.context.Title(),
                "iteration": destination.Title()
            }
        )

        try:
            destination.manage_pasteObjects(
                aq_parent(self.context).manage_cutObjects(
                    self.context.getId()))
        except:
            error = True
            message = _(u"An error occurred while moving")

        return {
            'action': 'drop',
            'message': {
                'type': 'info' if not error else 'error',
                'message': self.context.translate(message),
            },
            'error': error
        }
