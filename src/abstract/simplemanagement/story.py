from five import grok

from .interfaces import IStory


class View(grok.View):
    grok.context(IStory)
    grok.require('zope2.View')
