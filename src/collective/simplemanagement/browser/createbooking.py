from Products.Five.browser import BrowserView
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield.relation import create_relation
from datetime import datetime
from decimal import Decimal
import re


class CreateBookingView(BrowserView):

    def str_is_a_decimal_digit(self, string):
        return re.match("^[0-9]*\.?[0-9]+", string) != None

    def __call__(self):
        form = self.request.form

        self.convert_funcs = {
            'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
        }
        title = form.pop('title')
        date_str = form.pop('date')
        timespent = form.pop('time')
        day, month, year = date_str.split('/')
        date = datetime(int(year), int(month), int(day))

        if title and timespent:
            item = createContentInContainer(
                self.context,
                'Booking',
                title=title)
            for k, v in form.items():
                if v and k in self.convert_funcs:
                    v = self.convert_funcs[k](v)
                setattr(item, k, v)

            item.date = date
            if self.str_is_a_decimal_digit(timespent):
                item.time = Decimal(timespent)
            item.reindexObject()
