from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.memoize.instance import memoize

from ... import api
from ...configure import TRACKER_ID
from ...configure import DOCUMENTS_ID
from .view import View


class Overview(View):

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
        get_info = lambda x: {
            'title': x.Title, 'url': x.getURL,
            'description': x.Description,
            'date': to_local_time(x.modified, long_format=1),
            'class': 'contenttype-%s' % x.portal_type.lower()
        }
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
            get_info = lambda x: {
                'title': x.Title, 'url': x.getURL,
                'description': x.Description,
                'date': to_local_time(x.modified, long_format=1),
                'class': 'contenttype-%s' % x.portal_type.lower()
            }
            last_documents = [
                get_info(el) for el in
                last_stuff[:self.MAX_ELEMENTS + 1]
                if el.getPath != folder_path
            ]

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
                'user': api.users.get_user_details(self.context, i.user_id)
            }
