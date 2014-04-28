#-*- coding: utf-8 -*-

import json
from persistent import Persistent
from Acquisition import ImplicitAcquisitionWrapper

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

import plone.api

from .. import api
from ..interfaces import IBooking


@implementer(IBooking)
class Booking(Persistent):
    """ a Booking object.
    """

    cat_id = None
    uid = None
    # define getter/setter of attributes using zope schema for validation
    date = FieldProperty(IBooking['date'])
    time = FieldProperty(IBooking['time'])
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

    def __of__(self, parent):
        return ImplicitAcquisitionWrapper(self, parent)

    def index_references(self):
        references = self.references_dict
        uuids = set(references.values())
        # we indexes only the uid of the references
        return list(uuids)

    @property
    def references_dict(self):
        return dict(self.references)

    @property
    def project(self):
        return self.references_dict.get('Project')

    @property
    def story(self):
        return self.references_dict.get('Story')

    @property
    def ticket(self):
        return self.references_dict.get('ticket')

    _json_fields = (
        'uid',
        'date',
        'time',
        'text',
        'owner',
        'references_dict',
        'tags',
    )

    def as_dict(self):
        data = {}
        for k in self._json_fields:
            data[k] = getattr(self, k)
        data['references'] = data.pop('references_dict')
        return data

    def as_json(self):
        return json.dumps(self.as_dict(),
                          cls=api.jsonutils.ExtendedJSONEncoder)
