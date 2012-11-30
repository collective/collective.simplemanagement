from zope.component import getMultiAdapter

from plone.app.layout.dashboard import dashboard
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView


class DashboardMixin(object):
    query_extra_params = {
        'sort_on': 'modified',
        'sort_order': 'descending'
    }

    @memoize
    def tools(self):
        return {
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        }

    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    @property
    def user(self):
        user = None
        portal_state = self.portal_state()
        if not portal_state.anonymous():
            user = portal_state.member()
        return user

    def get_story(self, brain):
        story = brain.getObject()
        iteration = story.getParentNode()
        project = iteration.getParentNode()
        return {
            'title': brain.Title,
            'description': brain.Description,
            'url': brain.getURL(),
            'status': brain.review_state,
            'can_edit': story.user_can_edit(),
            'can_review': story.user_can_review(),
            'iteration': {
                'title': iteration.Title(),
                'description': iteration.Description(),
                'url': iteration.absolute_url()
            },
            'project': {
                'title': project.Title(),
                'description': project.Description(),
                'url': project.absolute_url()
            }
        }

    @property
    def searches(self):
        if self.portal_state().anonymous():
            return []

        return [
            ({'portal_type': 'PoiIssue',
              'getResponsibleManager': self.user.getId(),
              'review_state': ('new', 'open', 'in-progress', 'resolved',
                                'unconfirmed')},
             'tickets'),
            ({'portal_type': 'Story',
              'assigned_to': self.user.getId(),
              'review_state': ('todo', 'suspended', 'in_progress')},
              'stories')
        ]


class MyTickets(BrowserView, DashboardMixin):

    def tickets(self):
        query = self.searches[0][0]
        query.update(self.query_extra_params)
        pc = self.tools()['portal_catalog']
        return pc.searchResults(query)


class MyStories(BrowserView, DashboardMixin):

    def stories(self):
        query = self.searches[1][0]
        query.update(self.query_extra_params)
        pc = self.tools()['portal_catalog']
        return [self.get_story(i) for i in pc.searchResults(query)]


class DashboardView(dashboard.DashboardView, DashboardMixin):

    MAX_ELEMENTS = 5

    def format_results(self, brain, res_type):
        if res_type == 'tickets':
            return brain
        else:
            return self.get_story(brain)

    def dashboard(self):
        result = {
            'tickets': [],
            'tickets_n': 0,
            'stories': [],
            'stories_n': 0
        }

        pc = self.tools()['portal_catalog']
        for query, result_key in self.searches:
            query.update(self.query_extra_params)
            results = pc.searchResults(query)
            result[result_key] = [self.format_results(i, result_key) \
                for i in results[:self.MAX_ELEMENTS]]
            result['%s_n' % result_key] = total = len(results)
            if total <= self.MAX_ELEMENTS:
                result['%s_n' % result_key] = False
        return result
