from z3c.form import form, field

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from .. import api
from ..interfaces import IBooking
from ..interfaces import IQuickForm
from ..browser.widgets.time_widget import TimeFieldWidget


class BookingForm(form.AddForm):
    template = ViewPageTemplateFile("../browser/templates/quick_form.pt")

    @property
    def fields(self):
        fields = field.Fields(IQuickForm).select('text') + \
            field.Fields(IBooking).select('time') + \
            field.Fields(IBooking).select('date')
        fields['time'].widgetFactory = TimeFieldWidget
        return fields

    name = 'booking_form'

    def create(self, data):
        return api.booking.create_booking(self.context, data, reindex=False)

    def add(self, obj):
        obj.reindexObject()

    def nextURL(self):
        return self.context.absolute_url()

    def updateActions(self):
        super(BookingForm, self).updateActions()
        self.actions['add'].addClass("allowMultiSubmit")
