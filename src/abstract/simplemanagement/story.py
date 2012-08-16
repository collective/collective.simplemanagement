from datetime import date
from Acquisition import aq_inner
from zope import schema
from five import grok

from z3c.form import form, field
from z3c.form.interfaces import IFormLayer
from z3c.relationfield.relation import create_relation

from plone.z3cform import z2
from plone.dexterity.utils import createContentInContainer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
from .interfaces import IBooking
from .utils import get_timings
from .utils import get_user_details
from .utils import get_assignees_details
from . import messageFactory as _


class IBookingForm(IBooking):
    title = schema.TextLine(title=_(u"Title"))


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("story_templates/booking_form.pt")
    fields = field.Fields(IBookingForm).select('title', 'time', 'related')

    def create(self, data):
        convert_funcs = {
            'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
        }

        item = createContentInContainer(
            self.context,
            'Booking',
            title=data.pop('title'))
        for k, v in data.items():
            if k in convert_funcs:
                v = convert_funcs[k](v)
            setattr(item, k, v)
        item.date = date.today()
        return item

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()


class View(grok.View):
    grok.context(IStory)
    grok.require('zope2.View')

    def has_epic(self):
        return bool(self.context.epic) and not self.context.epic.isBroken()

    def timing(self):
        return get_timings(self.context)

    def get_assignees(self):
        return get_assignees_details(self.context)

    def booking_format(self, brain):
        obj = brain.getObject()
        booking = {
            'title': brain.Title,
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

        for el in catalog(**query):
            yield self.booking_format(el)

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
