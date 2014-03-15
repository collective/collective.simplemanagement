from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common as base
from .. import _


class OrderNumber(base.ViewletBase):

    index = ViewPageTemplateFile('templates/ordernumber.pt')

    def update(self):
        base.ViewletBase.update(self)
        self.order_number = self.context.order_number

    def available(self):
        return self.order_number is not None
