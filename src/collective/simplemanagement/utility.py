
from zope.interface import implements

from z3c.form import form, field

from . import _
from . import logger
from .booking import create_booking
from .interfaces import IMassiveBookingUploader
from .interfaces import IRowMassiveBookingUploader

class MassiveBookingUploader(object):
    implements(IMassiveBookingUploader)

    def uploade_event_list(self,context=None,events=[]):
        fields=field.Fields(IRowMassiveBookingUploader)
        keys=fields.keys()

        for row in events:            
            create_booking(context, data, reindex=False)
        
