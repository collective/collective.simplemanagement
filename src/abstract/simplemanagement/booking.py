from datetime import date

from five import grok
from z3c.form import form, field
from z3c.relationfield.relation import create_relation

from plone.directives import dexterity
from plone.dexterity.utils import createContentInContainer

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .interfaces import IBooking
from .interfaces import IQuickForm


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("story_templates/booking_form.pt")
    fields = field.Fields(IQuickForm).select('title') + \
            field.Fields(IBooking).select('time')

    name = 'booking_form'

    convert_funcs = {
        'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
    }

    def create(self, data):
        item = createContentInContainer(
            self.context,
            'Booking',
            title=data.pop('title'))
        for k, v in data.items():
            if v and k in self.convert_funcs:
                v = self.convert_funcs[k](v)
            setattr(item, k, v)
        item.date = date.today()
        return item

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()


class Booking(dexterity.Item):
    grok.implements(IBooking)

    def get_related(self):
        related = self.related
        if  bool(related) and \
            not related.isBroken():
            related = related.to_object
            return {
                'title': related.Title(),
                'href': related.absolute_url(),
                'description': related.Description(),
            }


class View(grok.View):
    grok.context(IBooking)
    grok.require('zope2.View')
