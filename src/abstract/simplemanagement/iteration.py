from five import grok

from .interfaces import IIteration


class View(grok.View):
    grok.context(IIteration)
    grok.require('zope2.View')
