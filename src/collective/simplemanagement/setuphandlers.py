from Products.CMFCore.utils import getToolByName
from . import messageFactory as _


def setupGroups(site):
    """
    Create Plone's default set of groups.
    """
    uf = getToolByName(site, 'acl_users')
    gtool = getToolByName(site, 'portal_groups')

    if not uf.searchGroups(id='PM'):
        title = site.translate(_(u'Project managers'))
        gtool.addGroup('PM', title=title, roles=['PM'])

    if not uf.searchGroups(id='employees'):
        title = site.translate(_(u"Employees"))
        gtool.addGroup('employees', title=title, roles=['Employee'])


def setupSimpleManagement(context):
    """Setup SimpleManagement step.
    """
    if context.readDataFile('collective-simplemanagement-install.txt') is None:
        return
    site = context.getSite()
    setupGroups(site)
