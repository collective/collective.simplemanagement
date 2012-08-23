from Acquisition import aq_inner
from five import grok

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

    def create(self, data):
        convert_funcs = {
            'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
        }

        item = createContentInContainer(
            self.context,
            'Story',
            title=data.pop('title'))
        for k, v in data.items():
            if v and k in convert_funcs:
                v = convert_funcs[k](v)
            setattr(item, k, v)
        # item.date = date.today()
        return item

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()


class Iteration(Container):
    grok.implements(IIteration)


class View(grok.View):
    grok.context(IIteration)
    grok.require('zope2.View')

    totals = None

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.context)
        stories = adpt.stories()
        self.totals = adpt.totals
        return stories

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = StoryForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
