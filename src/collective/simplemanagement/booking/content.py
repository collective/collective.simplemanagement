#-*- coding: utf-8 -*-

from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from ..interfaces import IBooking


class ReferenceDict(PersistentDict):
    """ a smarter persistent dict for our references
    """
    __allow_access_to_unprotected_subobjects__ = True


@implementer(IBooking)
class Booking(Persistent):
    """ a Booking object.
    """

    cat_id = None
    uid = None
    # define getter/setter of attributes using zope schema for validation
    date = FieldProperty(IBooking['date'])
    text = FieldProperty(IBooking['text'])
    owner = FieldProperty(IBooking['owner'])
    tags = FieldProperty(IBooking['tags'])

    def __init__(self, uid=None, date=None, time=None, text='',
                 owner='', references=None, tags=None):
        self.uid = uid
        self.date = date
        self.time = time
        self.text = text
        self.owner = owner
        # use PersistenDict to improve transaction
        # since they update only changed objects/values
        self.references = ReferenceDict(references or {})
        self.tags = set(tags or [])
