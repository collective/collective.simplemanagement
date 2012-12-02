from . import messageFactory as _


# TODO: these should be configurable via p.a.registry
TRACKER_ID = 'issues'
DOCUMENTS_ID = 'documents'
WARNING_DELTA = 3
MAN_DAY_HOURS = 8
WARNING_DELTA_PERCENT = 0.1


STATUS_ITEMS = [
    ('not_started', _(u'Not started')),
    ('analysis', _(u'Analysis')),
    ('offer', _(u'Offer')),
    ('development', _(u'Development')),
    ('staging', _(u'Staging')),
    ('production', _(u'Production')),
    ('maintenance', _(u'Maintenance')),
    ('dead', _(u'Dead'))
]


ENV_TYPES = [
    ('prototype', _(u'Prototype')),
    ('staging', _(u'Staging')),
    ('production', _(u'Production')),
]


ROLES = [
    ('account', _(u'Account')),
    ('project_manager', _(u'Project manager')),
    ('technical_lead', _(u'Technical lead')),
    ('developer', _(u'Developer')),
    ('designer', _(u'Designer')),
    ('sysadmin', _(u'Sysadmin'))
]
