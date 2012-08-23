from datetime import date
from Acquisition import aq_inner
from zope import schema
from five import grok

from z3c.form import form, field
from z3c.form.interfaces import IFormLayer
from z3c.relationfield.relation import create_relation

from plone.z3cform import z2
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.content import Container

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
from .interfaces import IBooking
from .interfaces import IQuickForm
from .utils import get_timings
from .utils import get_user_details
from .utils import get_assignees_details
from .utils import get_epic_by_story
from .utils import get_text


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("story_templates/booking_form.pt")
    fields = field.Fields(IQuickForm).select('title') + \
            field.Fields(IBooking).select('time')

    def create(self, data):
        convert_funcs = {
            'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
        }

        item = createContentInContainer(
            self.context,
            'Booking',
            title=data.pop('title'))
        for k, v in data.items():
            if v and k in convert_funcs:
                v = convert_funcs[k](v)
            setattr(item, k, v)
        item.date = date.today()
        return item

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()


class Story(Container):
    grok.implements(IStory)

    def get_text(self):
        return get_text(self, self.text)


class View(grok.View):
    grok.context(IStory)
    grok.require('zope2.View')

    def get_epic(self):
        return get_epic_by_story(self.context)

    def timing(self):
        return get_timings(self.context)

    def get_assignees(self):
        return get_assignees_details(self.context)

    def booking_format(self, brain):
        obj = brain.getObject()
        booking = {
            'title': brain.Title,
            'description': brain.Description,
            'time': brain.time,
            'href': brain.getURL(),
            'date': self.context.toLocalizedTime(brain.date.isoformat()),
            'related': obj.get_related(),
            'creator': get_user_details(self.context, brain.Creator)
        }
        return booking

    def get_booking(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': '/'.join(self.context.getPhysicalPath()),
            'object_provides': IBooking.__identifier__,
            'sort_on': 'booking_date'
        }

        return [self.booking_format(el) for el in catalog(**query)]

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
