from OFS.SimpleItem import SimpleItem
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from z3c.form.object import registerFactoryAdapter

from .interfaces import IResource, IEnvironment, IMilestone


class Resource(SimpleItem):

    implements(IResource)

    role = FieldProperty(IResource['role'])
    user_id = FieldProperty(IResource['user_id'])
    active = FieldProperty(IResource['active'])
    compass_effort = FieldProperty(IResource['compass_effort'])

    __name__ = None
    __parent__ = None

    def getId(self):
        return self.__name__ or ''


registerFactoryAdapter(IResource, Resource)


class Environment(SimpleItem):

    implements(IEnvironment)

    name = FieldProperty(IEnvironment['name'])
    env_type = FieldProperty(IEnvironment['env_type'])
    url = FieldProperty(IEnvironment['url'])

    __name__ = None
    __parent__ = None

    def getId(self):
        return self.__name__ or ''


registerFactoryAdapter(IEnvironment, Environment)


class Milestone(SimpleItem):

    implements(IMilestone)

    name = FieldProperty(IMilestone['name'])
    status = FieldProperty(IMilestone['status'])
    deadline = FieldProperty(IMilestone['deadline'])

    __name__ = None
    __parent__ = None

    def getId(self):
        return self.__name__ or ''


registerFactoryAdapter(IMilestone, Milestone)
