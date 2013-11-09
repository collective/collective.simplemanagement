import plone.api
from Acquisition import aq_inner

from zope.interface import implementer
from zope.security import checkPermission

from z3c.form.interfaces import IFormLayer
from z3c.form import form, field

from plone.z3cform import z2
from plone.dexterity.content import Container
from plone.dexterity.utils import createContentInContainer
from plone.app.dexterity.behaviors.metadata import ICategorization

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget
from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from .browser.widgets.time_widget import TimeFieldWidget
from .booking import BookingForm
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

    def get_actions(self):
        can_edit = self.user_can_edit()
        can_review = self.user_can_review()
        url = self.absolute_url()

        actions = [
            {
                "name": "quickView",
                "type": "overlay",
                "title": "Details",
                "description": "View details",
                "href": '{0}?nobook=1'.format(url),
                "css": "story-quickview",
            },

            {
                "name": "quickBooking",
                "type": "overlaybookingform",
                "description": "Booking",
                "css": "quick-booking",
                "href": url,
                "title": "Booking"
            },
        ]

        if can_edit:
            actions.extend(
                [
                    {
                        "name": "quickEdit",
                        "type": "overlayform",
                        "description": "Edit story",
                        "css": "quickedit",
                        "href": (
                            '{0}/quickedit?ajax_load=1&'
                            'ajax_include_head=1'.format(url)
                        ),
                        "title": "Edit"
                    },
                    {
                        "name": "changeIteration",
                        "type": "tooltip",
                        "description": "Change iteration",
                        "css": "iteration",
                        "href": '{0}/ch_iteration'.format(url),
                        "title": "Iteration"
                    },
                ]
            )

        if can_review:
            actions.append({
                "name": "changeStatus",
                "type": "tooltip",
                "description": "Change status",
                "css": "status",
                "href": '{0}/wf_actions'.format(url),
                "title": self.get_review_state()
            })

        return actions


class StoryQuickForm(form.AddForm):
    template = ViewPageTemplateFile("browser/templates/quick_form.pt")
    container = None
    description = _(
        u"When you add a story it will be put in the "
        u"first current iteration whether exists or in the project backlog")
    created = None

    @property
    def fields(self):
        fields = field.Fields(IQuickForm)
        fields += field.Fields(IStory).select(
            'estimate',
            'text',
            'assigned_to'
        )
        fields += field.Fields(ICategorization).select('subjects')
        fields['estimate'].widgetFactory = TimeFieldWidget
        fields['subjects'].widgetFactory = TokenInputFieldWidget
        fields['assigned_to'].widgetFactory = UserTokenInputFieldWidget
        return fields

    def create(self, data):
        self.created = api.content.create_story(
            self.context, data, reindex=False
        )
        return self.created

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        if self.request.HTTP_REFERER:
            return self.request.HTTP_REFERER

        return self.context.absolute_url()

    def updateWidgets(self):
        super(StoryQuickForm, self).updateWidgets()
        self.widgets['estimate'].hour_free_input = 1
        self.widgets['estimate'].show_min = 0

    def updateActions(self):
        super(StoryQuickForm, self).updateActions()
        self.actions['add'].addClass("allowMultiSubmit")


class ProjectStoryQuickForm(StoryQuickForm):

    def create(self, data):
        context = self.context
        if self.container:
            context = self.container
        # XXX: does it work?
        return self.create_story(context, data)

    def nextURL(self):
        if not self.container:
            return "%s/backlog" % self.context.absolute_url()
        if self.request.HTTP_REFERER:
            return self.request.HTTP_REFERER

        return self.context.absolute_url()
