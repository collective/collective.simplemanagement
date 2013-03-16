from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFPlone import PloneMessageFactory as _


class CustomerRole(object):
    implements(ISharingPageRole)
    title = _(u"Customer")
    required_permission = 'Manage portal content'


class EmployeeRole(object):
    implements(ISharingPageRole)
    title = _(u"Employee")
    required_permission = 'Manage portal content'


class PMRole(object):
    implements(ISharingPageRole)
    title = _(u"PM")
    required_permission = 'Manage portal content'
