from Acquisition import aq_inner
from five import grok

from zope.security import checkPermission
from z3c.form import form, field
from z3c.form.interfaces import IFormLayer
from z3c.relationfield.relation import create_relation

from plone.memoize.instance import memoize
from plone.dexterity.content import Container
from plone.dexterity.utils import createContentInContainer
from plone.z3cform import z2

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from abstract.z3cform.usertokeninput.widget import UserTokenInputFieldWidget

from .interfaces import IIteration
from .interfaces import IStoriesListing
from .interfaces import IQuickForm
from .interfaces import IStory


class StoryForm(form.AddForm):
    template = ViewPageTemplateFile("iteration_templates/story_form.pt")
    fields = field.Fields(IQuickForm) + field.Fields(IStory).select(
        'text',
        'estimate',
        'assigned_to',
        'epic')
    fields['assigned_to'].widgetFactory = UserTokenInputFieldWidget

    convert_funcs = {
            'epic': lambda x: create_relation('/'.join(x.getPhysicalPath()))
    }

    def create(self, data):
        item = createContentInContainer(
            self.context,
            'Story',
            title=data.pop('title'))
        for k, v in data.items():
            if v and k in self.convert_funcs:
                v = self.convert_funcs[k](v)
            setattr(item, k, v)
        return item

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()


class Iteration(Container):
    grok.implements(IIteration)


# XXX: move somewhere else
class IterationViewMixin(object):

    totals = None

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.context)
        stories = adpt.stories()
        self.totals = adpt.totals
        return stories

    def user_can_edit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def user_can_add_story(self):
        return checkPermission('cmf.AddPortalContent', self.context)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = StoryForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()


class View(grok.View, IterationViewMixin):
    grok.context(IIteration)
    grok.require('zope2.View')

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)
