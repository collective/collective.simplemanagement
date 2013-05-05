from Acquisition import aq_inner
from five import grok
from zope.security import checkPermission

from z3c.form.interfaces import IFormLayer
from z3c.form import form, field

from plone.z3cform import z2
from plone.dexterity.content import Container
from plone.dexterity.utils import createContentInContainer

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .booking import BookingForm
from .interfaces import IStory
from .interfaces import IQuickForm
from .utils import get_timings
from .utils import get_user_details
from .utils import get_assignees_details
from .utils import get_epic_by_story
from .utils import get_text
from .utils import get_project
from .utils import get_bookings
from . import messageFactory as _


def create_story(context, data, reindex=True):
    item = createContentInContainer(
        context,
        'Story',
        title=data.pop('title'))
    for k, v in data.items():
        setattr(item, k, v)
    if reindex:
        item.reindexObject()
    return item


class Story(Container):
    grok.implements(IStory)

    def get_milestone(self):
        if self.milestone:
            # XXX: This, bluntly put, sucks.
            project = get_project(self)
            for milestone in project.milestones:
                if self.milestone.decode('utf-8') == milestone.name:
                    return milestone
        return None

    def get_text(self):
        return get_text(self, self.text)

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


class View(grok.View):
    grok.context(IStory)
    grok.require('zope2.View')

    def user_can_booking(self):
        return checkPermission('simplemanagement.AddBooking', self.context)

    def get_epic(self):
        return get_epic_by_story(self.context)

    def timing(self):
        return get_timings(self.context)

    def get_assignees(self):
        return get_assignees_details(self.context)

    def booking_format(self, brain):
        obj = brain.getObject()
        description = brain.Description
        description = description and description.splitlines()
        booking = {
            'title': brain.Title,
            'description': description,
            'time': brain.time,
            'href': brain.getURL(),
            'date': self.context.toLocalizedTime(brain.date.isoformat()),
            'related': obj.get_related(),
            'creator': get_user_details(self.context, brain.Creator)
        }
        return booking

    def get_booking(self):
        return [self.booking_format(el)
                for el in get_bookings(project=self.context)]

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()


class StoryQuickForm(form.AddForm):
    template = ViewPageTemplateFile("browser/templates/quick_form.pt")
    fields = field.Fields(IQuickForm) + \
        field.Fields(IStory).select('estimate')
    container = None
    description = _(
        u"When you add a story it will be put in the "
        u"first current iteration whether exists or in the project backlog")

    def create(self, data):
        return create_story(self.context, data, reindex=False)

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        if self.request.HTTP_REFERER:
            return self.request.HTTP_REFERER

        return self.context.absolute_url()


class ProjectStoryQuickForm(StoryQuickForm):

    def create(self, data):
        context = self.context
        if self.container:
            context = self.container
        return self.create_story(context, data)

    def nextURL(self):
        if not self.container:
            return "%s/backlog" % self.context.absolute_url()
        if self.request.HTTP_REFERER:
            return self.request.HTTP_REFERER

        return self.context.absolute_url()
