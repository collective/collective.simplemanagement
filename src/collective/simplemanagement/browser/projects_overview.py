#-*- coding: utf-8 -*-

try:
    from collection import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from plone.app.search.browser import Search
from plone.app.search.browser import SortOption
from plone.memoize import view
from plone import api

from .. import _


class ProjectsOverview(Search):

    main_search_field = 'Title'
    forced_portal_types = ('Project',)
    allow_portal_types_filter = False
    # this allows for results with no query
    default_query = {
        'portal_type': 'Project',
        'review_state': [
            # use `list` because `tuple` breakes
            # zope `make_query` utils ;)
            'development',
            'maintenance',
            'offer',
            'planning',
        ],
        'sort_on': 'modified',
        'sort_order': 'reverse',
    }
    show_breadcrumbs = False
    updated_search_view_name = 'updated_projects_overview'

    _states_blacklist = ()

    display_fields = OrderedDict([
        ('Title', u'Title'),
        ('review_state', u'State'),
        ('modified', u'Date'),
    ])

    def sort_options(self):
        """ Sorting options for search results view. """
        return (
            SortOption(
                self.request,
                _(u'modified (inv)'),
                sortkey='modified',
                search_view=self,
                reverse=1,
            ),
            SortOption(
                self.request,
                _(u'alphabetically'),
                sortkey='sortable_title',
                search_view=self,
            ),
            SortOption(
                self.request,
                _(u'alphabetically (inv)'),
                sortkey='sortable_title',
                search_view=self,
                reverse=1,
            )
        )

    @property
    def wftool(self):
        wftool = api.portal.get_tool('portal_workflow')
        return wftool

    @view.memoize_contextless
    def _review_states(self):
        states_blacklist = self._states_blacklist
        wf_id = self.wftool.getChainForPortalType(
            self.default_query['portal_type'])[0]
        wf = self.wftool[wf_id]
        return [{'name': x.id, 'title': x.title}
                for x in wf.states.objectValues()
                if x.id not in states_blacklist]

    def review_states(self):
        items = []
        for item in self._review_states():
            selected = item['name'] in self.request.get('review_state')
            selected = selected or \
                item['name'] in self.default_query.get('review_state', [])
            item['selected'] = selected
            items.append(item)
        return items

    @property
    def _display_converters(self):
        plone_view = self.context.restrictedTraverse('@@plone')
        get_date = lambda ob, value, **kw: plone_view.toLocalizedTime(value)
        # get_state_display comes from ViewMixin
        get_state = lambda ob, value, **kw: self.get_state_display(ob, value)
        return {
            # klass converters
            'datetime': get_date,
            'DateTime': get_date,
            'review_state': get_state,
        }

    def get_display_values(self, brain):
        # defaults to brain attributes
        data = {}
        # @@search view actually returns CatalogContentListingObject
        brain = brain._brain
        default_converter = lambda ob, value: value
        for k in self.display_fields.iterkeys():
            if hasattr(brain, k):
                value = getattr(brain, k, None)
                converter = self._display_converters.get(k)
                if converter is None:
                    # look for klass converter
                    klass_name = value.__class__.__name__
                    converter = self._display_converters.get(klass_name,
                                                             default_converter)
                data[k] = converter(brain, value)
        # insert always these
        data['title'] = brain.Title
        data['url'] = brain.getURL()
        data['review_state'] = brain.review_state
        return data

    def get_state_display(self, brain, value):
        _type = brain.portal_type
        return self.wftool.getTitleForStateOnType(value, _type)
