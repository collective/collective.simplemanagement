import re
import json
from urllib import urlencode

from zope.interface import implementsOnly, implementer
from zope.component import adapter
from zope.schema.interfaces import IField

from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import Widget
from z3c.form.widget import FieldWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.browser.widget import HTMLTextInputWidget
from z3c.form.browser.widget import addFieldClass
from z3c.form.browser.text import TextWidget

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.uuid.utils import uuidToObject
from plone import api

from ... import _
from ...api.content import get_project
from ...api.content import BreadcrumbGetter
from ...api.booking import get_storage
from .interfaces import IBookWidget
from .interfaces import IReferencesWidget
from .interfaces import ITagsWidget


ELECTRIC_CHARS = {
    '@': ('Project', 'Story'),
    '*': ('PoiIssue',),
    '#': None
}

ELECTRIC_CHARS_FIELD = {
    '@': 'references',
    '*': 'references',
    '#': 'tags'
}

VALID_CHARS = '[\\w\\.\\-]'

REGEXP = re.compile(
    '({electric})({id}+)'.format(
        electric='|'.join(re.escape(c) for c in ELECTRIC_CHARS),
        id=VALID_CHARS
    )
)

TEMPLATE = ('<a class="booking-text ref-link portaltype-{class_}" '
            'href="{url}">{tag}</a>')
TEMPLATE_NOTFOUND = ('<em>{tag}</em>')


def format_text(booking, context=None):
    """ return formatted text for booking.
    It renders booking text as rich text with links to resources
    """
    references = [
        r for r in (
            booking.references if booking.references is not None else []
        )
    ]

    def format_tag(m):
        tag = m.group(0)
        url = None
        css_class = 'none'
        ref = None
        bookings_context = context
        if ELECTRIC_CHARS[m.group(1)] is None:
            if bookings_context is None:
                bookings_context = api.portal.get()
            url = bookings_context.absolute_url() + '/bookings/?' + urlencode({
                'tags:list': [m.group(2)]
            }, True)
        else:
            object_ = None
            try:
                ref = references.pop(0)
                object_ = uuidToObject(ref[1])
            except IndexError:
                pass
            finally:
                if object_ is None:
                    if ref is not None:
                        references.insert(0, ref)
                else:
                    css_class = ref[0].lower()
                    url = object_.absolute_url()
        if url:
            return TEMPLATE.format(url=url, tag=tag, class_=css_class)
        return TEMPLATE_NOTFOUND.format(tag=tag)
    result = REGEXP.sub(format_tag, booking.text)
    return result


class BookWidget(HTMLTextInputWidget, Widget):
    implementsOnly(IBookWidget)

    klass = u"book-widget"
    css = u'text'
    value = u''
    size = 55
    references_field = None
    tags_field = None
    valid_chars = VALID_CHARS
    base_electric_chars = ELECTRIC_CHARS
    placeholder = _(u'@project @story *ticket #tag activity')

    js_messages = {
        'no_completions': _(u"No completions"),
        'broken_message': _(u"We found broken references. "
                            u"Please recheck your booking before submit.")
    }

    @property
    def autocomplete_url(self):
        return api.portal.get().absolute_url() + '/@@booking-autocomplete'

    @property
    def electric_chars(self):
        return json.dumps({
            k: v for k, v in self.base_electric_chars.items()
                if v is None or len(v) > 0
        })

    @property
    def references_selector(self):
        if self.references_field is None:
            return None
        return 'input[name="{name}"]'.format(name=self.references_field)

    @property
    def tags_selector(self):
        if self.tags_field is None:
            return None
        return 'input[name="{name}"]'.format(name=self.tags_field)

    def update(self):
        super(BookWidget, self).update()
        addFieldClass(self)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def BookFieldWidget(field, request):
    """IFieldWidget factory for BookWidget."""
    return FieldWidget(field, BookWidget(request))


class ReferencesWidget(TextWidget):

    implementsOnly(IReferencesWidget)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def ReferencesFieldWidget(field, request):
    """IFieldWidget factory for ReferencesWidget."""
    return FieldWidget(field, ReferencesWidget(request))


class TagsWidget(TextWidget):

    implementsOnly(ITagsWidget)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def TagsFieldWidget(field, request):
    """IFieldWidget factory for TagsWidget."""
    return FieldWidget(field, TagsWidget(request))


class ReferencesConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        widget_value = []
        if isinstance(value, (list, tuple)):
            for item in value:
                item_value = {
                    'portal_type': item[0],
                    'uuid': item[1]
                }
                if len(item) > 2:
                    item_value['frozen'] = bool(item[2])
                widget_value.append(item_value)
        return json.dumps(widget_value)

    def toFieldValue(self, value):
        field_value = []
        if value:
            value = json.loads(value)
            for item in value:
                field_value.append(
                    (
                        item['portal_type'].encode('utf-8'),
                        item['uuid'].encode('utf-8')
                    )
                )
        return field_value


class TagsConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        widget_value = []
        if isinstance(value, (list, tuple, set)):
            for item in value:
                widget_value.append(item)
        return json.dumps(widget_value)


    def toFieldValue(self, value):
        field_value = set()
        if value:
            field_value = set(json.loads(value))
        return field_value


class Autocomplete(BrowserView):

    MAX_RESULTS = 50
    MIN_QUERY = 1

    @staticmethod
    def next_query(value):
        if len(value) > 0:
            value = value[:-1] + chr(ord(value[-1])+1)
        return value

    def search_tags(self, query, results):
        storage = get_storage()
        tags = storage.vocabulary('tags')
        for tag in tags:
            if query in tag:
                results.append({
                    'portal_type': None,
                    'uuid': tag,
                    'title': tag,
                    'id': tag,
                    'breadcrumb': None
                })
        if query not in [ r['id'] for r in results ]:
            results.append({
                'portal_type': None,
                'uuid': query,
                'title': query,
                'id': query,
                'breadcrumb': None
            })

    def search_content(self, query, portal_type, results):
        kwargs = {
            'getId': { 'query': (query, self.next_query(query)),
                       'range': 'min:max' },
            'portal_type': portal_type,
            'sort_on': 'id'
        }
        filter_context = self.request.form.get('filter_context')
        frozen_refs = self.request.form.get('frozen_refs')
        exclude_uuids = set()
        if filter_context or frozen_refs:
            if filter_context:
                filter_context = json.loads(filter_context)
            else:
                filter_context = []
            if frozen_refs:
                filter_context += json.loads(frozen_refs)
            project = None
            for item in filter_context:
                exclude_uuids.add(item['uuid'])
                if item['portal_type'] == 'Project':
                    project = uuidToObject(item['uuid'])
                    break
                else:
                    story = uuidToObject(item['uuid'])
                    project = get_project(story)
            if project is not None:
                kwargs['portal_type'] = ('Story',)
                kwargs['path'] = {
                    'query': '/'.join(project.getPhysicalPath())
                }
        catalog = getToolByName(self.context, 'portal_catalog')
        get_breadcrumb = BreadcrumbGetter(catalog)
        brains = catalog.searchResults(**kwargs)
        brains = brains[:self.MAX_RESULTS]
        for brain in brains:
            if brain['UID'] not in exclude_uuids:
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

