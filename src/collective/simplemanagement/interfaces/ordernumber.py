from zope import schema
from zope.interface import alsoProvides
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model

from .. import _


class IOrderNumber(model.Schema):

    order_number = schema.TextLine(
        title=_(u"Order number"),
        required=False
    )


alsoProvides(IOrderNumber, IFormFieldProvider)
