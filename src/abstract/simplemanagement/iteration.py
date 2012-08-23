from five import grok
from plone.memoize.instance import memoize
from plone.dexterity.content import Container

from .interfaces import IIteration
from .interfaces import IStoriesListing


class Iteration(Container):
    grok.implements(IIteration)


class View(grok.View):
    grok.context(IIteration)
    grok.require('zope2.View')

    totals = None

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.context)
        stories = adpt.stories()
        self.totals = adpt.totals
        return stories

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)
