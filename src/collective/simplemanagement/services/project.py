from datetime import date
import plone.api
from zope.security import checkPermission

from datetime import date
from .. import api
from ..interfaces import IStoriesListing
from . import base


class JSONService(base.JSONService):

    def _get_stories(self, iteration):
        adpt = IStoriesListing(iteration)(actions_filter=[
            "quickView",
            "quickBooking",
            "quickEdit",
            "changeStatus"
        ])
        return adpt.totals, adpt.stories

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

        totals, stories = self._get_stories(item)

        return {
            "title": item.title,
            "description": item.description,
            "url": item.absolute_url(),
            'status': 'TODO',  # TODO: get iteration status and display it
            "stories": [],  # retrieved dynamically
            "is_sortable": self.user_can_manage_project(item),
            "start": start,
            "start_str": self.context.toLocalizedTime(start),
            "end": end,
            "end_str": self.context.toLocalizedTime(end),
            "can_edit": checkPermission('cmf.ModifyPortalContent', item),
            "warning_delta_percent": self._settings.warning_delta_percent,
            "totals": totals
        }

    @api.permissions.accesscontrol("View")
    def view(self):
        iterations = {
            'past': [],
            'current': [],
            'future': []
        }
        now = date.today()
        for brain in self._get_iterations():
            obj = brain.getObject()
            if obj.end < now:
                iterations['past'].append(self._format_iteration(obj))
            elif obj.end >= now and obj.start <= now:
                iterations['current'].append(self._format_iteration(obj))
            else:
                iterations['future'].append(self._format_iteration(obj))

        return {
            "title": self.context.title,
            "description": self.context.description,
            "iterations": iterations
        }
