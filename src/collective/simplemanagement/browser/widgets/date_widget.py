from zope.interface import implementsOnly, implementer
from zope.component import adapter
from zope.schema.interfaces import IField
from z3c.form.interfaces import IFieldWidget, IFormLayer
from z3c.form.converter import DateDataConverter
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser.widget import HTMLTextInputWidget

from .. import api
from .interfaces import IBookingDateWidget


class BookingDateDataConverter(DateDataConverter):

    length = 'short'


class BookingDateWidget(HTMLTextInputWidget, Widget):

    implementsOnly(IBookingDateWidget)

    klass = 'date-widget full'

    def pattern(self):
        formatter = self.request.locale.dates.getFormatter("date", "short")
        pattern = formatter.getPattern()
        return pattern.lower().replace('yy', 'y')

    def formatted_value(self):
        if not self.value:
            return ''
        return api.date.timeago(self.value)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def BookingDateFieldWidget(field, request):
    """IFieldWidget factory for BookingDateWidget."""
    return FieldWidget(field, BookingDateWidget(request))
