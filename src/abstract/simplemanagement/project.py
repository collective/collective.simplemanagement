from datetime import date
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from five import grok
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

from .interfaces import IProject
from .configure import DOCUMENTS_ID
from .utils import get_user_details


class View(grok.View):
    grok.context(IProject)
    grok.require('zope2.View')

    MAX_ELEMENTS = 5

    @memoize
    def status_vocabulary(self):
        name = "abstract.simplemanagement.status"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_milestone_status(self, value):
        voc = self.status_vocabulary()
        return voc.getTermByToken(value).title

    @memoize
    def roles_vocabulary(self):
        name = "abstract.simplemanagement.roles"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_role(self, value):
        voc = self.roles_vocabulary()
        return voc.getTermByToken(value).title

    @memoize
    def env_vocabulary(self):
        name = "abstract.simplemanagement.envtypes"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_env_type(self, value):
        voc = self.env_vocabulary()
        return voc.getTermByToken(value).title

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
        now = date.today()
        for iteration_brain in raw_iterations:
            iteration = iteration_brain.getObject()
            if iteration.end < now:
                iterations['past'].append(iteration)
            elif iteration.end >= now and iteration.start <= now:
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
            folder_path = '/'.join(documents_folder.getPhysicalPath())
            last_stuff = pc.searchResults({
                'path': folder_path,
                'sort_on': 'modified',
                'sort_order': 'descending'
            })
            for item in last_stuff[:self.MAX_ELEMENTS + 1]:
                if item.getPath() != folder_path:
                    last_documents.append(item)
        return {
            'last': last_documents,
            'folder': documents_folder
        }

    def operatives(self):
        for i in self.context.operatives:
            yield  {
                'role': self.get_role(i.role),
                'user': get_user_details(self.context, i.user_id)
            }

class OverView(View):
    grok.context(IProject)
    grok.name('overview')
    grok.require('zope2.View')

