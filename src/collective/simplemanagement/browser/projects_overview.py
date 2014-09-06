#-*- coding: utf-8 -*-

from plone.app.search.browser import Search


class ProjectsOverview(Search):

    main_search_field = 'Title'
    forced_portal_types = ('Project',)
    allow_portal_types_filter = False
    # this allows for results with no query
    default_query = {'portal_type': 'Project'}
