from z3c.form.form import Form
from plone.z3cform.layout import wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ...booking.form import BookingForm
from ... import _


class BookingBarForm(BookingForm):

    def action(self):
        return self.context.absolute_url() + '/@@booking_bar'

    def render(self):
        if self._finishedAdd:
            self.ignoreRequest = True
            self.updateWidgets()
            return Form.render(self)
        return super(BookingBarForm, self).render()

    def add(self, __):
        self.status = _(u"Booking was succesfully added!")


BookingBarView = wrap_form(
    BookingBarForm,
    index=ViewPageTemplateFile('templates/booking_bar.pt')
)
