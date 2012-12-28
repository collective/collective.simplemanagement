from zope.interface import implements
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from .interfaces import ISettings


TIMELINE_ANNOTATIONS_KEY = 'collective.simplemanagement.timeline'
TRACKER_ID = 'issues'
DOCUMENTS_ID = 'documents'


class Settings(object):

    implements(ISettings)

    _vocabularies = (
        'statuses',
        'env_types',
        'resource_roles',
        'off_duty_reasons'
    )

    def __init__(self):
        self.storage = getUtility(IRegistry).forInterface(ISettings)

    def __getattr__(self, name):
        if name in self._vocabularies:
            return [
                tuple(line.split("|", 1)) for line in \
                    getattr(self.storage, name)
            ]
        return getattr(self.storage, name)
