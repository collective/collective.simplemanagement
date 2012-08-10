from five import grok

from .interfaces import IBooking


class View(grok.View):
    grok.context(IBooking)
    grok.require('zope2.View')

    def has_related(self):
        return bool(self.context.related) and \
            not self.context.related.isBroken()
