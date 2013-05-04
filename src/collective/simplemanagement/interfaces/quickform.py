from zope.interface import Interface
from zope import schema

from .. import _


class IQuickForm(Interface):
    title = schema.TextLine(
        title=_(u'Title'),
    )
