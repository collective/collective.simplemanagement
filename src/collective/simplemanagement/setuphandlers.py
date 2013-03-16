from Products.CMFCore.utils import getToolByName


def setupGroups(site):
    """
    Create Plone's default set of groups.
    """
    uf = getToolByName(site, 'acl_users')
    gtool = getToolByName(site, 'portal_groups')
    if not uf.searchGroups(id='PM'):
        gtool.addGroup('PM', title='Project managers',
                       roles=['PM'])

    if not uf.searchGroups(id='Employee'):
        gtool.addGroup('Employee', title='Employee', roles=['Employee'])


def setupSimpleManagement(context):
    """Setup SimpleManagement step.
    """
    if context.readDataFile('collective-simplemanagement-install.txt') is None:
        return
    site = context.getSite()
    setupGroups(site)
