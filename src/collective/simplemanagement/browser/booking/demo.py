from Acquisition import aq_inner
from plone.z3cform import z2
from z3c.form.interfaces import IFormLayer
from Products.Five.browser import BrowserView

from ...booking import BookingForm


class DemoView(BrowserView):

    def form_contents(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = BookingForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()
