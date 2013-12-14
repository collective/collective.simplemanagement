import plone.api

from zope.interface import implementer
from zope.security import checkPermission

from plone.dexterity.content import Container

from Products.CMFCore.utils import getToolByName


from .interfaces import IStory
from .interfaces import IQuickForm
from . import api
from . import messageFactory as _


@implementer(IStory)
class Story(Container):

    def get_milestone(self):
        if self.milestone:
            # XXX: This, bluntly put, sucks.
            project = api.content.get_project(self)
            for milestone in project.milestones:
                if self.milestone.decode('utf-8') == milestone.name:
                    return milestone
        return None

    def get_text(self):
        return api.text.get_text(self, self.text)

    def user_can_edit(self):
        return checkPermission('cmf.ModifyPortalContent', self)

    def user_can_review(self):
        """An user can review a story if at least one WF transition
        is available
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        wf = wf_tool.getWorkflowsFor(self)
        if wf:
            wf = wf[0]
        actions = wf.listActionInfos(object=self, max=1)
        return len(actions) > 0

    def get_review_state(self):
        return plone.api.content.get_state(obj=self)

    def get_actions(self, actions_filter=[
            "quickView",
            "quickBooking",
            "quickEdit",
            "changeIteration",
            "changeStatus"
    ]):

        can_edit = self.user_can_edit()
        can_review = self.user_can_review()
        url = self.absolute_url()

        actions = []

        if "quickView" in actions_filter:
            actions.append({
                "name": "quickView",
                "type": "overlay",
                "title": "Details",
                "description": "View details",
                "href": '{0}?nobook=1'.format(url),
                "css": "story-quickview",
            })

        if "quickBooking" in actions_filter:
            actions.append({
                "name": "quickBooking",
                "type": "overlaybookingform",
                "description": "Booking",
                "css": "quick-booking",
                "href": url,
                "title": "Booking"
            })

        if can_edit:
            if 'quickEdit' in actions_filter:
                actions.append({
                    "name": "quickEdit",
                    "type": "overlayform",
                    "description": "Edit story",
                    "css": "quickedit",
                    "href": (
                        '{0}/quickedit?ajax_load=1&'
                        'ajax_include_head=1'.format(url)
                    ),
                    "title": "Edit"
                })

            if "changeIteration" in actions_filter:
                actions.append({
                    "name": "changeIteration",
                    "type": "tooltip",
                    "description": "Change iteration",
                    "css": "iteration",
                    "href": '{0}/ch_iteration'.format(url),
                    "title": "Iteration"
                })

        if can_review and "changeStatus" in actions_filter:
            actions.append({
                "name": "changeStatus",
                "type": "tooltip",
                "description": "Change status",
                "css": "status",
                "href": '{0}/wf_actions'.format(url),
                "title": self.get_review_state()
            })

        return actions
