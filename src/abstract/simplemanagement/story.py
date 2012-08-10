from five import grok

from .interfaces import IStory
from .utils import get_timings


class View(grok.View):
    grok.context(IStory)
    grok.require('zope2.View')

    def has_epic(self):
        return bool(self.context.epic) and not self.context.epic.isBroken()

    def timing(self):
        return get_timings(self.context)
