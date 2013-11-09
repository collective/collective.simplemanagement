from datetime import date

from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from ...interfaces import IStoriesListing
from ... import messageFactory as _


class Planning(BrowserView):

    @memoize
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @memoize
    def get_iterations(self, mode='left'):
        iterations = [
            {
                'title': _(u"Backlog"),
                'uuid': IUUID(self.context),
                'selected': False
            }
        ]
        if mode == 'left':
            iterations[0]['selected'] = True
        pc = self.portal_catalog()
        raw_iterations = pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Iteration',
            'sort_on': 'start',
            'sort_order': 'ascending'
        })
        now = date.today()
        selected = None
        for iteration_brain in raw_iterations:
            data = {
                'title': iteration_brain.Title,
                'uuid': iteration_brain.UID,
                'selected': False
            }
            # on the right pane, either select the current iteration,
            # or the first future one
            if mode == 'right' and selected is None:
                iteration = iteration_brain.getObject()
                if iteration.end >= now and iteration.start <= now:
                    data['selected'] = True
                    selected = iteration
                elif iteration.start > now and selected is None:
                    data['selected'] = True
                    selected = iteration
            iterations.append(data)
        return iterations


class Stories(BrowserView):

    @memoize
    def uuid(self):
        return self.request['iteration']

    @memoize
    def widget_id(self):
        return self.request['widget_id']

    @memoize
    def iteration(self):
        return uuidToObject(self.uuid())

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.iteration())()
        return adpt.stories

    @memoize
    def totals(self):
        adpt = IStoriesListing(self.iteration())()
        return adpt.totals
