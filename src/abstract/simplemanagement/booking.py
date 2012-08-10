from five import grok

from .interfaces import IBooking


class View(grok.View):
    grok.context(IBooking)
    grok.require('zope2.View')
