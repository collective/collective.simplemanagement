from decimal import Decimal

from zope.interface import implementsOnly, implementer
from zope.component import adapter
from zope.schema.interfaces import IField
from zope.schema.fieldproperty import FieldProperty

from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import Widget
from z3c.form.widget import FieldWidget
from z3c.form.browser.widget import HTMLTextInputWidget
from z3c.form.converter import DecimalDataConverter

from .interfaces import ITimeWidget


class TimeWidget(HTMLTextInputWidget, Widget):
    implementsOnly(ITimeWidget)
    klass = u"time-widget"
    show_min = FieldProperty(ITimeWidget['show_min'])
    hour_free_input = FieldProperty(ITimeWidget['hour_free_input'])
    hour_start = FieldProperty(ITimeWidget['hour_start'])
    hour_stop = FieldProperty(ITimeWidget['hour_stop'])

    @property
    def current_hour(self):
        value = getattr(self.context, self.__name__, None)
        if value is not None:
            # return only integer part
            return int(value)
        return None

    @property
    def current_minute(self):
        value = getattr(self.context, self.__name__, None)
        if value is not None:
            # get decimal part
            value = value - int(value)
            # convert to minutes
            value = value * Decimal('60')
            return int(value)
        return None

    def hours(self):
        hour = self.current_hour
        for i in xrange(self.hour_start, self.hour_stop + 1):
            item = {
                'value': i,
                'selected': hour == i
            }
            yield item

    def minutes(self):
        minute = self.current_minute
        for i in range(15, 60, 15):
            item = {
                'value': i,
                'selected': minute == i
            }
            yield item

    def extract(self, default=""):
        hour = self.request.get(self.name + '-hour', '0')
        minute = self.request.get(self.name + '-minute', '0')
        return '%s|%s' % (hour, minute)


@adapter(IField, IFormLayer)
@implementer(IFieldWidget)
def TimeFieldWidget(field, request):
    """IFieldWidget factory for TimeWidget."""
    return FieldWidget(field, TimeWidget(request))


class TimeConverter(DecimalDataConverter):

    def toWidgetValue(self, value):
        # import pdb;pdb.set_trace()
        # res = super(self.__class__, self).toWidgetValue(value)
        # print res
        pass

    def toFieldValue(self, value):
        hour, minute = value.split('|')

        # minute o hour could be empty string
        if not hour:
            hour = 0
        if not minute:
            minute = 0
        # min are in 1/60 we need to transform it to 1/100
        _minute = Decimal(minute) / Decimal('60')
        res = Decimal(hour) + _minute
        return res
