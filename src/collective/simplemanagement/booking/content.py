#-*- coding: utf-8 -*-

from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOSet

from zope.interface import implementer

from .interfaces import IBooking
from .utils import AttrDict


class ReferenceDict(PersistentDict, AttrDict):
    """ a smarter persistent dict for our references
    """
    __allow_access_to_unprotected_subobjects__ = True


@implementer(IBooking)
class Booking(Persistent):
    """ a Booking object.
    """

    def __init__(self, date=None, time=None, text='',
                 owner='', references={}, tags=[]):
        self.date = date
        self.time = time
        self.text = text
        self.owner = owner
        # use PersistenDict and OOSet to improve transaction
        # since they update only changed objects/values
        assert isinstance(references, dict)
        assert isinstance(tags, (tuple, list, set))
        self.references = ReferenceDict(references)
        self.tags = OOSet(tags)
