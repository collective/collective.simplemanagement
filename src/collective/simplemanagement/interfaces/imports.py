
from zope import schema

from .. import _
from . import IQuickForm
from . import IBooking

class IRowMassiveBookingUploader(IQuickForm,IBooking):
      project = schema.TextLine(
          title=_(u"Project"),
          required=True
      )

      story = schema.TextLine(
          title=_(u"Story"),
          required=True
      )
      