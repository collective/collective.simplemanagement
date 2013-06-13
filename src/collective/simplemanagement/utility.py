
from zope.interface import implements

from . import _
from . import logger
from .interfaces import IMassiveBookingUploader

class MassiveBookingUploader(object):
    implements(IMassiveBookingUploader)

    def uploade_event_list(self,parent=None,events=[]):
        pass
