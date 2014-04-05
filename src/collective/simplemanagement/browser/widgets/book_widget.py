import json

from zope.interface import implementsOnly, implementer
from zope.component import adapter
from zope.schema.interfaces import IField

from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import Widget
from z3c.form.widget import FieldWidget
from z3c.form.browser.widget import HTMLTextInputWidget
from z3c.form.browser.widget import addFieldClass

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.uuid.utils import uuidToObject
from plone import api

from ...api.content import get_project
from ...api.content import BreadcrumbGetter
from .interfaces import IBookWidget


ELECTRIC_CHARS = {
    '@': ('Project', 'Story'),
    '!': ('PoiIssue',),
    '#': None
}


class BookWidget(HTMLTextInputWidget, Widget):
    implementsOnly(IBookWidget)

    klass = u"book-widget"
    css = u'text'
    value = u''
    size = 45

    @property
    def autocomplete_url(self):
        return api.portal.get().absolute_url() + '/@@booking-autocomplete'

    @property
    def electric_chars(self):
        return json.dumps({ k: k for k in ELECTRIC_CHARS })

    def update(self):
        super(BookWidget, self).update()
        addFieldClass(self)

    def extract(self, default=""):
        return self.request.get(self.name, default)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def BookFieldWidget(field, request):
    """IFieldWidget factory for BookWidget."""
    return FieldWidget(field, BookWidget(request))


class Autocomplete(BrowserView):

    MAX_RESULTS = 50
    MIN_QUERY = 1

    def search_tags(self, query, results):
        # BBB: use real values
        tags = [
            'foo',
            'bar',
            'spam',
            'eggs'
        ]
        results = []
        for tag in tags:
            if query in tag:
                results.append({
                    'portal_type': None,
                    'uuid': tag,
                    'title': tag,
                    'id': tag,
                    'breadcrumb': None
                })
        results.append({
            'portal_type': None,
            'uuid': query,
            'title': query,
            'id': query,
            'breadcrumb': None
        })
        return results

    def search_content(self, query, portal_type, results):
        kwargs = {
            'Title': query + '*',
            'portal_type': portal_type
        }
        filter_context = self.request.form.get('filter_context')
        if filter_context:
            filter_context = json.loads(filter_context)
            project = None
            for item in filter_context:
                if item['portal_type'] == 'Project':
                    project = uuidToObject(item['uuid'])
                    break
                else:
                    story = uuidToObject(item['uuid'])
                    project = get_project(story)
            if project is not None:
                kwargs['path'] = {
                    'query': '/'.join(project.getPhysicalPath())
                }
        catalog = getToolByName(self.context, 'portal_catalog')
        get_breadcrumb = BreadcrumbGetter(catalog)
        brains = catalog.searchResults(**kwargs)
        brains = brains[:self.MAX_RESULTS]
        for brain in brains:
            results.append({
                'portal_type': brain['portal_type'],
                'uuid': brain['UID'],
                'title': brain['Title'].decode('utf-8'),
                'id': brain['id'],
                'breadcrumb': get_breadcrumb(brain)
            })

    def __call__(self):
        # filter=['#', '12']
        # filter_context=[{"portal_type": "Project", "uuid": "uuid"}]
        filter = json.loads(self.request.form['filter'])
        electric_char, query = filter
        portal_type = ELECTRIC_CHARS[electric_char]
        results = []
        if len(query) >= self.MIN_QUERY:
            if portal_type is None:
                # search on tags
                self.search_tags(query, results)
            else:
                self.search_content(query, portal_type, results)
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(results)

