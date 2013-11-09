from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from ...interfaces import IStoriesListing
from .base import IterationViewMixin


class View(BrowserView, IterationViewMixin):

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)
