import os.path
import pkg_resources
import plone.api
from OFS.Image import Image

try:
    pkg_resources.get_distribution('collective.transmogrifier')
except pkg_resources.DistributionNotFound:
    HAS_TRANSMOGRIFIER = False
else:
    from collective.transmogrifier.transmogrifier import Transmogrifier
    HAS_TRANSMOGRIFIER = True


TEST_USERS = [
    {
        'username': 'employee1',
        'password': 'employee1',
        'group': 'employees',
        'email': 'employee1@example.com',
        'fullname': 'Cary Grant',
        'portrait': 'cary.jpg'
    },
    {
        'username': 'employee2',
        'password': 'employee2',
        'group': 'employees',
        'email': 'employee2@example.com',
        'fullname': 'Greta Garbo',
        'portrait': 'greta.jpg'
    },
    {
        'username': 'employee3',
        'password': 'employee3',
        'group': 'employees',
        'email': 'employee3@example.com',
        'fullname': 'Audrey Hepburn',
        'portrait': 'audrey.jpg'
    },
    {
        'username': 'pm1',
        'password': 'pm1',
        'group': 'employees',
        'email': 'pm1@example.com',
        'fullname': 'Humphrey Bogart',
        'portrait': 'humphrey.jpg'
    }
]


def create_users(context):
    if context.readDataFile('loadcontent_various.txt') is None:
        return

    portal = context.getSite()
    pr = plone.api.portal.get_tool(name='portal_registration')
    pg = plone.api.portal.get_tool(name='portal_groups')
    pm = plone.api.portal.get_tool(name='portal_membership')
    pmd = plone.api.portal.get_tool(name='portal_memberdata')

    for user_data in TEST_USERS:
        username, password, group, portrait = (
            user_data.pop('username', None),
            user_data.pop('password', None),
            user_data.pop('group', None),
            user_data.pop('portrait', None)
        )
        if username not in portal.acl_users.getUserIds():
            try:
                pr.addMember(username, password)
                if group:
                    pg.addPrincipalToGroup(username, group)
                user = pm.getMemberById(username)
                user.setMemberProperties(mapping=user_data)
                if portrait:
                    portrait_file = open(
                        os.path.join(
                            os.path.dirname(__file__),
                            'data',
                            portrait
                        ),
                        'rb'
                    )
                    pmd._setPortrait(
                        Image(id=username,
                              file=portrait_file,
                              title=user_data['fullname']),
                        username
                    )
                    portrait_file.close()
            except ValueError:
                logger.warn('The login name "%s" is not valid.' % username)
            except KeyError:
                logger.warn('The group "%s" is not valid.' % group)
    return 'Users created'


def load_content(context):
    if context.readDataFile('loadcontent_various.txt') is None:
        return
    portal = context.getSite()
    if HAS_TRANSMOGRIFIER:
        transmogrifier = Transmogrifier(portal)
        transmogrifier(u'loadcontent')
        return 'Imported content types...'
    return 'Please install collective.transmogrifier to use this import step'
