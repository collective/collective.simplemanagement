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

    # volatile attributes for acquisition
    _v_name = None
    _v_parent = None

    @property
    def __name__(self):
        return self._v_name

    @__name__.setter
    def __name__(self, value):
        self._v_name = value

    @property
    def __parent__(self):
        return self._v_parent

    @__parent__.setter
    def __parent__(self, value):
        self._v_parent = value

    def __of__(self, parent):
        return ImplicitAcquisitionWrapper(self, parent)

    @property
    def __ac_local_roles__(self):
        parent = self.__parent__
        if parent is None:
            parent = plone.api.portal.get()
        local_roles = {}
        if hasattr(parent, '__ac_local_roles__'):
            if callable(parent.__ac_local_roles__):
                local_roles = parent.__ac_local_roles__()
            else:
                local_roles = parent.__ac_local_roles__
        for roles in local_roles.values():
            if 'Owner' in roles:
                roles.remove('Owner')
        local_roles.setdefault(self.owner, []).append('Owner')
        return local_roles

    # Without this, the cache of borg.localrole gets confused
    # when we inherit the physical path from the container,
    # therefore gets all the cached values of the container.
    # Normally this does not happen (say on edit form)
    # because the cache stores in the request,
    # and doesn't calcuate local roles for parent.
    def getPhysicalPath(self):
        if self.__parent__ is not None:
            return self.__parent__.getPhysicalPath() + (self.uid,)
        # Yeah, we need this.
        raise AttributeError('getPhysicalPath')

    @property
    def title(self):
        return self.text

    def Title(self):
        return self.title

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
