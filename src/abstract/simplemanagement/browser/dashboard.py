from zope.component import getMultiAdapter
from plone.app.layout.dashboard import dashboard
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName


class DashboardView(dashboard.DashboardView):

    MAX_ELEMENTS = 5

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
                ({'portal_type': 'PoiIssue',
                  'getResponsibleManager': user.getId(),
                  'review_state': ('new', 'open', 'in-progress', 'resolved',
                                    'unconfirmed')},
                 'tickets'),
                ({'portal_type': 'Story',
                  'assigned_to': user.getId(),
                  'review_state': ('todo', 'suspended', 'in_progress')},
                  'stories')
            ]
            for query, result_key in searches:
                query.update({
                    'path': '/'.join(self.context.getPhysicalPath()),
                    'sort_on': 'modified',
                    'sort_order': 'descending'
                })
                results = pc.searchResults(query)
                result[result_key] = results[:self.MAX_ELEMENTS]
                result['%s_n' % result_key] = total = len(results)
                if total <= self.MAX_ELEMENTS:
                    result['%s_n' % result_key] = False
        return result
