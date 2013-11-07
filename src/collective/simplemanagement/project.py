from Acquisition import aq_inner
from datetime import date
from zope.interface import implementer
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.security import checkPermission

from z3c.form.interfaces import IFormLayer

from five import grok
from plone.z3cform import z2

from plone.memoize.instance import memoize
from plone.dexterity.content import Container
from Products.CMFCore.utils import getToolByName
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject

from .interfaces import IProject, IStoriesListing, IBacklogView
from .configure import DOCUMENTS_ID, TRACKER_ID
from .utils import get_user_details
from .utils import get_text
from .utils import AttrDict
from .browser.iteration import IterationViewMixin
from .story import ProjectStoryQuickForm
from . import messageFactory as _


@implementer(IProject)
class Project(Container):

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

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    def user_can_add_story(self):
        return checkPermission('simplemanagement.AddStory', self.context)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = ProjectStoryQuickForm(
            aq_inner(self.context),
            self.request
        )
        iterations = self.iterations()
        if iterations and iterations['current']:
            addform.container = iterations['current'][0]
        addform.update()
        return addform.render()

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


class AllIterations(View):
    grok.context(IProject)
    grok.name('alliterations')
    grok.require('zope2.View')


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

    def tracker_url(self):
        project_tracker = self.context.restrictedTraverse(TRACKER_ID, None)
        if project_tracker:
            return project_tracker.absolute_url()

    def last_activities(self):
        project_path = '/'.join(self.context.getPhysicalPath())

        pc = self.tools['portal_catalog']
        last_stuff = pc.searchResults({
            'path': project_path,
            'portal_type': ['Story', 'Iteration', 'Epic', 'PoiIssue'],
            'sort_on': 'modified',
            'sort_order': 'descending'
        })
        to_local_time = self.context.toLocalizedTime
        get_info = lambda x: {'title': x.Title, 'url': x.getURL,
                            'description': x.Description,
                            'date': to_local_time(x.modified, long_format=1),
                            'class': 'contenttype-%s' % x.portal_type.lower()}
        return [get_info(el) for el in last_stuff[:11]]

    def documents(self):
        last_documents = []
        documents_folder_url = []
        documents_folder = self.context.restrictedTraverse(DOCUMENTS_ID, None)
        if documents_folder:
            documents_folder_url = documents_folder.absolute_url()
            folder_path = '/'.join(documents_folder.getPhysicalPath())

            pc = self.tools['portal_catalog']
            last_stuff = pc.searchResults({
                'path': folder_path,
                'sort_on': 'modified',
                'sort_order': 'descending'
            })

            to_local_time = self.context.toLocalizedTime
            get_info = lambda x: {'title': x.Title, 'url': x.getURL,
                            'description': x.Description,
                            'date': to_local_time(x.modified, long_format=1),
                            'class': 'contenttype-%s' % x.portal_type.lower()}
            last_documents = [get_info(el) for el in
                               last_stuff[:self.MAX_ELEMENTS + 1]
                               if el.getPath != folder_path]

        return {'last': last_documents,
                'folder_url': documents_folder_url
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


@implementer(IBacklogView)
class Backlog(grok.View, IterationViewMixin):
    grok.context(IProject)
    grok.require('cmf.ModifyPortalContent')
    grok.name('backlog')
