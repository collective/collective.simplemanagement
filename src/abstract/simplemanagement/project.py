from datetime import datetime
from zope.component import getMultiAdapter
from five import grok
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

from .interfaces import IProject
from .configure import DOCUMENTS_ID


class View(grok.View):
    grok.context(IProject)
    grok.require('zope2.View')

    MAX_ELEMENTS = 5

    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    @memoize
    def tools(self):
        return {
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        }

    def dashboard(self):
        result = {
            'tickets': [],
            'tickets_n': 0,
            'stories': [],
            'stories_n': 0
        }
        portal_state = self.portal_state()
        if not portal_state.anonymous():
            user = portal_state.member()
            pc = self.tools()['portal_catalog']
            searches = [
                ({ 'portal_type': 'PoiIssue',
                   'getResponsibleManager': user.getId(),
                   'review_state': ('new', 'open', 'in-progress', 'resolved',
                                    'unconfirmed') },
                 'tickets'),
                ({ 'portal_type': 'Story',
                   'assigned_to': user.getId(),
                   'review_state': ('todo', 'suspended', 'in_progress') },
                 'stories')
            ]
            for query, result_key in searches:
                query.update({
                    'path': '/'.join(self.context.getPhysicalPath())
                })
                results = pc.searchResults(query)
                result[result_key] = results[:self.MAX_ELEMENTS]
                result['%s_n' % result_key] = total = len(results)
                if total <= self.MAX_ELEMENTS:
                    result['%s_n' % result_key] = False
        return result

    def iterations(self):
        iterations = {
            'past': [],
            'current': [],
            'future': []
        }
        pc = self.tools()['portal_catalog']
        raw_iterations = pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Iteration',
            'sort_on': 'start',
            'sort_order': 'ascending'
        })
        now = datetime.now()
        for iteration_brain in raw_iterations:
            iteration = iteration_brain.getObject()
            if iteration.end < now:
                iterations['past'].append(iteration)
            elif iteration.end >= now and iteration.start < now:
                iterations['current'].append(iteration)
            else:
                iterations['future'].append(iteration)
        return iterations

    def documents(self):
        last_documents = []
        documents_folder = None
        if DOCUMENTS_ID in self.context:
            documents_folder = self.context[DOCUMENTS_ID]
            pc = self.tools()['portal_catalog']
            last_stuff = pc.searchResults({
                'path': '/'.join(documents_folder.getPhysicalPath()),
                'sort_on': 'modified',
                'sort_order': 'descending'
            })
            for item in last_stuff[:self.MAX_ELEMENTS]:
                last_documents.append(item)
        return {
            'last': last_documents,
            'folder': documents_folder
        }
