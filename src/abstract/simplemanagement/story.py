from Acquisition import aq_inner
from five import grok

from z3c.form.interfaces import IFormLayer

from plone.z3cform import z2

from plone.dexterity.content import Container

from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
from .interfaces import IBooking
from .booking import BookingForm

from .utils import get_timings
from .utils import get_user_details
from .utils import get_assignees_details
from .utils import get_epic_by_story
from .utils import get_text


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
