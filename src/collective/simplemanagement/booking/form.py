#-*- coding: utf-8 -*-

import itertools
from datetime import date
from collections import defaultdict

from zope.component import getMultiAdapter
from zope.schema import ValidationError

from z3c.form import form
from z3c.form import button
from z3c.form import field
from z3c.form import interfaces

from plone.uuid.interfaces import IUUID

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api as plone_api
from Products.CMFCore.utils import getToolByName
from plone.app.uuid.utils import uuidToCatalogBrain
from .. import _
from .. import api
from ..interfaces import IBooking
from ..interfaces import IStory
from ..interfaces import IProject
from ..browser.widgets.time_widget import TimeFieldWidget
from ..browser.widgets.book_widget import BookFieldWidget
from ..browser.widgets.book_widget import ReferencesFieldWidget
from ..browser.widgets.book_widget import TagsFieldWidget
from ..browser.widgets.book_widget import REGEXP
from ..browser.widgets.book_widget import ELECTRIC_CHARS
from ..browser.widgets.book_widget import ELECTRIC_CHARS_FIELD


def get_prefix(form_):
    prefix = 'booking-contextless.'
    if form_.context:
        try:
            prefix = 'booking-' + IUUID(form_.context) + '.'
        except TypeError:
            prefix = 'booking-nouid.'
    return prefix


class ParsingError(ValidationError):

    def doc(self):
        return self.args[0]


def only_father_children(couples):
    """Returns only couples of father, children or children, father brains.

    Couples is a list of (brain1, brain2) tuples.
    Returns an iterable where only couples where brain1 is child of brain2
    or brain2 is child of brain1 are kept.

    Duplicates (e.g. A,B and B,A) are merged (only A,B is returned).
    Also, elements A,A are not kept.
    """
    found_couples = set()
    for left, right in couples:
        left_path = left.getPath()
        right_path = right.getPath()
        if left_path.rstrip('/') == right_path.rstrip('/'):
            continue
        elif left_path.startswith(right_path):
            couple_id = '%s:%s' % (right.UID, left.UID)
            if couple_id not in found_couples:
                found_couples.add(couple_id)
                yield (right, left)
        elif right_path.startswith(left_path):
            couple_id = '%s:%s' % (left.UID, right.UID)
            if couple_id not in found_couples:
                found_couples.add(couple_id)
                yield (right, left)


class ParseActor(object):
    """The poor man's adapter for acting upon parsed data.

    Calls the appropriate do_ method for the various fields.

    Its responsibility is to fix up what is submitted.
    It tries to resolve everything that javascript skipped over.
    """

    def __init__(self, form_, data, errors):
        self.portal_catalog = getToolByName(
            plone_api.portal.get(),
            'portal_catalog'
        )
        self.form = form_
        self.data = data
        self.errors = errors
        references = data.get('references')
        references = references if references else []
        self.references = [
            (k, uuidToCatalogBrain(v)) for k, v in references
        ]

    def make_error(self, message):
        error = ParsingError(message)
        view = getMultiAdapter(
            (error, self.form.request,
             self.form.widgets['text'],
             self.form.widgets['text'].field,
             self.form, self.form.getContent()),
            interfaces.IErrorViewSnippet
        )
        view.update()
        self.errors += (view,)

    def raw_find(self, ptype, path, id_):
        portal_type = ptype if isinstance(ptype, (list, tuple)) else (ptype,)
        query = {
            'portal_type': portal_type,
            'getId': id_
        }
        if path is not None and path['mode'] == 'parent':
            query['path'] = path['path']
        results = self.portal_catalog.searchResults(**query)
        if path is not None and path['mode'] == 'child':
            return [
                b for b in results if path['path'].startswith(b.getPath())
            ]
        return results

    def find(self, ptype, path, id_):
        results = self.raw_find(ptype, path, id_)
        if len(results) > 1:
            self.make_error(_(u'Ambiguous reference "%s"') % id_)
        elif len(results) == 0:
            self.make_error(_(u'Missing reference "%s"') % id_)
        else:
            return results[0]
        return None

    def ptype_in_references(self, ptype):
        for reference in self.references:
            if reference['value'][0] == ptype:
                return reference['value'][1]
        return None

    def resolve_projects_and_stories(self, unresolved):
        if len(unresolved) == 2:
            # we have two tokens, either a story, project or project, story
            results_1 = self.raw_find(
                ('Project', 'Story'),
                None,
                unresolved[0]['hint']['id']
            )
            results_2 = self.raw_find(
                ('Project', 'Story'),
                None,
                unresolved[1]['hint']['id']
            )
            results = [
                c for c in only_father_children(
                    itertools.product(results_1, results_2)
                )
            ]
            if len(results) > 1:
                self.make_error(
                    _(u'Ambiguous references: "%s", "%s"') % (
                        unresolved[0]['hint']['id'],
                        unresolved[1]['hint']['id']
                    )
                )
            elif len(results) == 0:
                self.make_error(
                    _(u'Missing references: "%s", "%s"') % (
                        unresolved[0]['hint']['id'],
                        unresolved[1]['hint']['id']
                    )
                )
            else:
                result = results[0]
                unresolved[0]['value'] = (result[0].portal_type, result[0])
                unresolved[1]['value'] = (result[1].portal_type, result[1])
        elif len(unresolved) == 1:
            # single token, either project or story
            result = self.find(
                ('Project', 'Story'),
                None,
                unresolved[0]['hint']['id']
            )
            if result is not None:
                unresolved[0]['value'] = (result.portal_type, result)

    def cleanup_projects_and_stories(self, references):
        unresolved = []
        for reference in references:
            project = self.ptype_in_references('Project')
            story = self.ptype_in_references('Story')
            if project is not None and story is not None:
                self.make_error(_(u"Multiple conflicting '@' references"))
                break
            elif project is not None:
                # it must be a story
                result = self.find(
                    'Story',
                    { 'path': project.getPath(),
                      'mode': 'parent' },
                    reference['hint']['id']
                )
                if result is not None:
                    reference['value'] = ('Story', result)
            elif story is not None:
                # must be a project
                result = self.find(
                    'Project',
                    { 'path': story.getPath(),
                      'mode': 'child' },
                    reference['hint']['id']
                )
                if result is not None:
                    reference['value'] = ('Project', result)
            else:
                # could be a project or a story
                unresolved.append(reference)
        if len(unresolved) > 0:
            self.resolve_projects_and_stories(unresolved)

    def cleanup_tickets(self, references):
        project = self.ptype_in_references('Project')
        for reference in references:
            result = self.find(
                'PoiIssue',
                { 'path': project.getPath(),
                  'mode': 'parent' },
                reference['hint']['id']
            )
            if result is not None:
                reference['value'] = ('PoiIssue', result)

    def do_references(self, tokens):
        new_references = []
        for char, token in tokens:
            if len(self.references) > 0 and \
                        self.references[0][1].getId == token:
                # Okay, this has been found
                new_references.append({
                    'value': self.references.pop(0)
                })
            else:
                new_references.append({
                    'value': (None, None),
                    'hint': {
                        'type': ELECTRIC_CHARS[char],
                        'id': token
                    }
                })
        self.references = new_references
        self.cleanup_projects_and_stories(
            r for r in self.references
                if r['value'][0] is None and
                        ('Story' in r['hint']['type'] or
                         'Project' in r['hint']['type'])
        )
        self.cleanup_tickets(
            r for r in self.references
                if r['value'][0] is None and
                        'PoiIssue' in r['hint']['type']
        )
        refs_by_type = defaultdict(lambda: 0)
        self.data['references'] = []
        for reference in self.references:
            type_ = reference['value'][0]
            if type_ is not None:
                refs_by_type[type_] = refs_by_type[type_] + 1
                self.data['references'].append(
                    (type_, reference['value'][1].UID)
                )
        for ptype in ['Project', 'Story']:
            if refs_by_type[ptype] > 1:
                self.make_error(_(u"Multiple conflicting '@' references"))

    def do_tags(self, tokens):
        if 'tags' in self.data:
            for __, token in tokens:
                self.data['tags'].add(token)

    def parse(self):
        if 'text' in self.data:
            parsed_data = {}
            for char, token in REGEXP.findall(self.data['text']):
                parsed_data.setdefault(
                    ELECTRIC_CHARS_FIELD[char],
                    []
                ).append((char, token))
            for field_ in parsed_data:
                mname = 'do_' + field_
                if hasattr(self, mname):
                    m = getattr(self, mname)
                    if callable(m):
                        m(parsed_data[field_])
        return (self.data, self.errors)


def elchar_strip(electric_chars, *ptypes):
    for key, value in electric_chars.items():
        if value is not None:
            value = list(value)
            for ptype in ptypes:
                if ptype in value:
                    value.remove(ptype)
                    if len(value) > 0:
                        electric_chars[key] = value
                    else:
                        del electric_chars[key]
    return electric_chars


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("../browser/templates/quick_form.pt")

    name = 'booking_form'

    def extractData(self, setErrors=True):
        data, errors = super(BookingForm, self).extractData(
            setErrors=setErrors
        )
        if IStory.providedBy(self.context):
            project = api.content.get_project(self.context)
            data['text'] = u'@{project} @{story} '.format(
                project=project.getId(),
                story=self.context.getId()
            ) + data.get('text', u'')
        elif IProject.providedBy(self.context):
            data['text'] = u'@{project} '.format(
                project=self.context.getId()
            ) + data.get('text', u'')
        return ParseActor(self, data, errors).parse()

    @property
    def fields(self):
        fields = field.Fields(IBooking).select('text') + \
            field.Fields(IBooking).select('time') + \
            field.Fields(IBooking).select('date') + \
            field.Fields(IBooking).select('references') + \
            field.Fields(IBooking).select('tags')
        fields['time'].widgetFactory = TimeFieldWidget
        fields['text'].widgetFactory = BookFieldWidget
        fields['references'].widgetFactory = ReferencesFieldWidget
        fields['tags'].widgetFactory = TagsFieldWidget
        return fields

    def create(self, data):
        # Trims to the right as suggested by Giorgio
        data['text'] = data['text'].rstrip()
        if 'owner' not in data and not plone_api.user.is_anonymous():
            data['owner'] = plone_api.user.get_current().id
        return api.booking.create_booking(**data)

    def add(self, obj):
        pass

    def nextURL(self):
        return self.context.absolute_url()

    def updateActions(self):
        super(BookingForm, self).updateActions()
        self.actions['add'].addClass("allowMultiSubmit")

    def updateWidgets(self):
        prefix = get_prefix(self)
        super(BookingForm, self).updateWidgets(prefix=prefix)
        defaults = {
            'date': date.today()
        }
        text_widget = self.widgets['text']
        electric_chars = {
            k: v for k, v in text_widget.base_electric_chars.items()
        }
        if IStory.providedBy(self.context):
            text_widget.base_electric_chars = elchar_strip(
                electric_chars,
                'Project',
                'Story'
            )
            project = api.content.get_project(self.context)
            defaults.update({
                'references': [
                    ('Project', IUUID(project), True),
                    ('Story', IUUID(self.context), True)
                ]
            })
            text_widget.placeholder = _(u"*ticket #tag activity")
        elif IProject.providedBy(self.context):
            text_widget.base_electric_chars = elchar_strip(
                electric_chars,
                'Story'
            )
            defaults.update({
                'references': [
                    ('Project', IUUID(self.context), True)
                ]
            })
            text_widget.placeholder = _(u"@story *ticket #tag activity")
        for name, widget in self.widgets.items():
            if name in defaults:
                converter = interfaces.IDataConverter(widget)
                widget.value = converter.toWidgetValue(defaults[name])
            if name == 'text':
                widget.references_field = self.widgets['references'].name
                widget.tags_field = self.widgets['tags'].name
            if name in ['references', 'tags']:
                widget.mode = interfaces.HIDDEN_MODE


class EditForm(form.EditForm):

    name = 'booking_edit_form'

    noChangesMessage = _(u"No changes were applied.")
    successMessage = _(u'Data successfully updated.')
    deleteMessage = _(u'Booking succesfully deleted.')

    def extractData(self, setErrors=True):
        data, errors = super(EditForm, self).extractData(
            setErrors=setErrors
        )
        return ParseActor(self, data, errors).parse()

    @property
    def fields(self):
        fields = field.Fields(IBooking).select('text') + \
            field.Fields(IBooking).select('time') + \
            field.Fields(IBooking).select('date') + \
            field.Fields(IBooking).select('references') + \
            field.Fields(IBooking).select('tags')
        fields['time'].widgetFactory = TimeFieldWidget
        fields['text'].widgetFactory = BookFieldWidget
        fields['references'].widgetFactory = ReferencesFieldWidget
        fields['tags'].widgetFactory = TagsFieldWidget
        return fields

    def updateWidgets(self):
        prefix = get_prefix(self)
        super(EditForm, self).updateWidgets(prefix=prefix)
        for name, widget in self.widgets.items():
            if name == 'text':
                widget.references_field = self.widgets['references'].name
                widget.tags_field = self.widgets['tags'].name
            if name in ['references', 'tags']:
                widget.mode = interfaces.HIDDEN_MODE

    def redirect(self):
        helpers = getMultiAdapter((self.context, self.request),
                                  name='helpers')
        self.request.response.redirect(helpers.view_url())

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

        plone_api.portal.show_message(message=self.status,
                                      request=self.request)
        storage = api.booking.get_storage()
        storage.reindex(self.context)
        self.redirect()

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        plone_api.portal.show_message(message=self.noChangesMessage,
                                      request=self.request)
        self.redirect()

    @button.buttonAndHandler(_(u'Delete booking'), name='delete-booking')
    def handleDelete(self, action):
        helpers = getMultiAdapter((self.context, self.request),
                                  name='helpers')
        parent_url = helpers.parent_url
        storage = api.booking.get_storage()
        storage.delete(self.context.uid)
        plone_api.portal.show_message(message=self.deleteMessage,
                                      request=self.request)
        self.request.response.redirect(parent_url)

