#-*- coding: utf-8 -*-

from datetime import date

from z3c.form import form
from z3c.form import button
from z3c.form import field
from z3c.form import interfaces

from plone.uuid.interfaces import IUUID

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api as plone_api
from .. import _
from .. import api
from ..interfaces import IBooking
from ..interfaces import IStory
from ..interfaces import IProject
from ..browser.widgets.time_widget import TimeFieldWidget
from ..browser.widgets.book_widget import BookFieldWidget
from ..browser.widgets.book_widget import ReferencesFieldWidget
from ..browser.widgets.book_widget import TagsFieldWidget


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("../browser/templates/quick_form.pt")

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

    name = 'booking_form'

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
        super(BookingForm, self).updateWidgets()
        defaults = {
            'date': date.today()
        }
        if IStory.providedBy(self.context):
            project = api.content.get_project(self.context)
            defaults.update({
                'text': '@{project} @{story} '.format(
                    project=project.getId(),
                    story=self.context.getId()
                ),
                'references': [
                    ('Project', IUUID(project)),
                    ('Story', IUUID(self.context))
                ]
            })
        elif IProject.providedBy(self.context):
            defaults.update({
                'text': '@{project} '.format(
                    project=self.context.getId()
                ),
                'references': [
                    ('Project', IUUID(self.context))
                ]
            })
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
    name = 'booking-edit-form'
    fields = field.Fields(IBooking)

    noChangesMessage = _(u"No changes were applied.")
    successMessage = _(u'Data successfully updated.')

    def redirect(self):
        self.request.response.redirect(
            location=self.context.absolute_url()
        )

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

        plone_api.portal.show_message(message=self.status)
        self.redirect()

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        plone_api.portal.show_message(message=self.status)
        self.redirect()
