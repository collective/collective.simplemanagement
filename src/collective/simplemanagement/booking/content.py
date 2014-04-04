#-*- coding: utf-8 -*-

from persistent import Persistent
from persistent.dict import PersistentDict
from BTrees.OOBTree import OOSet

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

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

    # define getter/setter of attributes using zope schema
    uuid = FieldProperty(IBooking['uuid'])
    date = FieldProperty(IBooking['date'])
    text = FieldProperty(IBooking['text'])
    owner = FieldProperty(IBooking['owner'])
    tags = FieldProperty(IBooking['tags'])

    def __init__(self, uuid=0L, date=None, time=None, text='',
                 owner='', references={}, tags=[]):
        self.uuid = uuid
        self.date = date
        self.time = time
        self.text = text
        self.owner = owner
        # use PersistenDict and OOSet to improve transaction
        # since they update only changed objects/values
        self.references = ReferenceDict(references)
        self.tags = OOSet(tags)
