from datetime import date
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from five import grok
from plone.memoize.instance import memoize
from plone.dexterity.content import Container
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from .interfaces import IProject, IStoriesListing, IBacklogView
from .configure import DOCUMENTS_ID
from .utils import get_user_details
from .utils import get_text
from .utils import AttrDict
from .iteration import IterationViewMixin
from . import messageFactory as _


class Project(Container):
    grok.implements(IProject)

    def get_notes(self):
        notes = self.notes
        if notes:
            return self.notes.output


class View(grok.View):
    grok.context(IProject)
    grok.require('zope2.View')

    @property
    @memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        })

    def iterations(self):
        iterations = {
            'past': [],
            'current': [],
            'future': []
        }
        pc = self.tools['portal_catalog']
        raw_iterations = pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Iteration',
            'sort_on': 'start',
            'sort_order': 'ascending'
        })
        now = date.today()
        have_iterations = False
        for iteration_brain in raw_iterations:
            iteration = iteration_brain.getObject()
            if iteration.end < now:
                iterations['past'].append(iteration)
                have_iterations = True
            elif iteration.end >= now and iteration.start <= now:
                iterations['current'].append(iteration)
                have_iterations = True
            else:
                iterations['future'].append(iteration)
                have_iterations = True
        if not have_iterations:
            return None
        return iterations


class OverView(View):
    grok.context(IProject)
    grok.name('overview')
    grok.require('zope2.View')

    MAX_ELEMENTS = 5

    @memoize
    def status_vocabulary(self):
        name = "collective.simplemanagement.status"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_milestone_status(self, value):
        voc = self.status_vocabulary()
        return voc.getTermByToken(value).title

    @memoize
    def roles_vocabulary(self):
        name = "collective.simplemanagement.roles"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_role(self, value):
        voc = self.roles_vocabulary()
        return voc.getTermByToken(value).title

    @memoize
    def env_vocabulary(self):
        name = "collective.simplemanagement.envtypes"
        return getUtility(IVocabularyFactory, name)(self.context)

    def get_env_type(self, value):
        voc = self.env_vocabulary()
        return voc.getTermByToken(value).title

    def documents(self):
        last_documents = []
        documents_folder = None
        if DOCUMENTS_ID in self.context:
            # documents_folder = self.context[DOCUMENTS_ID]
            # XXX: tryiing to resolve document folder raises a
            # unauthorized error when a user doesn't have view
            # permissions
            document_folder_path = list(self.context.getPhysicalPath())
            document_folder_path.append(DOCUMENTS_ID)

            pc = self.tools['portal_catalog']
            folder_path = '/'.join(document_folder_path)
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
        operatives = self.context.operatives
        if not operatives:
            operatives = []

        for i in operatives:
            yield  {
                'role': self.get_role(i.role),
                'user': get_user_details(self.context, i.user_id)
            }


class Planning(grok.View):
    grok.context(IProject)
    grok.require('cmf.ModifyPortalContent')
    grok.name('planning')

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


class Stories(grok.View):
    grok.context(IProject)
    grok.require('cmf.ModifyPortalContent')
    grok.name('stories')

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
        adpt = IStoriesListing(self.iteration())
        return adpt.stories()


class Backlog(grok.View, IterationViewMixin):
    grok.implements(IBacklogView)
    grok.context(IProject)
    grok.require('cmf.ModifyPortalContent')
    grok.name('backlog')
