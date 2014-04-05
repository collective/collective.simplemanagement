#-*- coding: utf-8 -*-

from persistent import Persistent

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from ..interfaces import IBooking


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
    references = FieldProperty(IBooking['references'])
    tags = FieldProperty(IBooking['tags'])

    def __init__(self, uid=None, date=None, time=None, text='',
                 owner='', references=None, tags=None):
        self.uid = uid
        self.date = date
        self.time = time
        self.text = text
        self.owner = owner
        self.references = list(references or [])
        self.tags = set(sorted(tags or []))

    def index_references(self):
        # we indexes only the uid of the references
        return [x[1] for x in self.references]

    @property
    def references_dict(self):
        return dict(self.references)

    @property
    def project(self):
        return self.references_dict.get('project')

    @property
    def story(self):
        return self.references_dict.get('story')

    @property
    def ticket(self):
        return self.references_dict.get('ticket')
