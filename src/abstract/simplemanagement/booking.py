from five import grok
from plone.directives import dexterity
from .interfaces import IBooking


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
