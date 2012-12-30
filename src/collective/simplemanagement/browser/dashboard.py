from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ..interfaces import IMyStoriesListing


class DashboardMixin(BrowserView):

    @memoize
    def tools(self):
        return {
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        }

    @memoize
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')

    @property
    def user(self):
        user = None
        portal_state = self.portal_state()
        if not portal_state.anonymous():
            user = portal_state.member()
        return user


class MyTickets(DashboardMixin):

    @property
    def _query(self):
        return {
            'portal_type': 'PoiIssue',
            'getResponsibleManager': self.user.getId(),
            'review_state': ('new', 'open', 'in-progress', 'unconfirmed'),
            'sort_on': 'modified',
            'sort_order': 'descending'
        }
        # 'resolved',

    def tickets(self):
        pc = self.tools()['portal_catalog']
        return pc.searchResults(self._query)


class MyStories(DashboardMixin):
    pass


class DashboardView(DashboardMixin):

    def projects(self):
        listing = IMyStoriesListing(self.context)

        projects = {}
        for st in listing.stories(project_info=True):
            prj = st.pop('project')
            if prj['UID'] not in projects:
                projects[prj['UID']] = prj
                projects[prj['UID']]['stories'] = []

            projects[prj['UID']]['stories'].append(st)

        projects = [p[1] for p in projects.items()]
        projects.sort(key=lambda x: x['priority'])
        return projects
