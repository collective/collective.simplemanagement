#-*- coding: utf-8 -*-

from plone.app.search.browser import Search
from plone.memoize import view
from plone import api


class ProjectsOverview(Search):

    main_search_field = 'Title'
    forced_portal_types = ('Project',)
    allow_portal_types_filter = False
    # this allows for results with no query
    default_query = {'portal_type': 'Project'}
    show_breadcrumbs = False

    _states_blacklist = ()

    @view.memoize_contextless
    def review_states(self):
        states_blacklist = self._states_blacklist
        wftool = api.portal.get_tool('portal_workflow')
        wf_id = wftool.getChainForPortalType(
            self.default_query['portal_type'])[0]
        wf = wftool[wf_id]
        return [{'name': x.id, 'title': x.title}
                for x in wf.states.objectValues()
                if x.id not in states_blacklist]

