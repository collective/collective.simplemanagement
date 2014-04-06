from z3c.form import form, field, interfaces

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .. import api
from ..interfaces import IBooking
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
        for name, widget in self.widgets.items():
            if name == 'text':
                widget.references_field = self.widgets['references'].name
                widget.tags_field = self.widgets['tags'].name
            if name in ['references', 'tags']:
                widget.mode = interfaces.HIDDEN_MODE
