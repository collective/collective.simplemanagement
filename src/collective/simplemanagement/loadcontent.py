import re
import os.path
from datetime import date, timedelta

import pkg_resources

from OFS.Image import Image
from Products.CMFPlone.utils import getToolByName

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


def unicodize(val):
    if isinstance(val, unicode):
        return val
    return val.decode('utf-8')


def create_users(context):
    if context.readDataFile('loadcontent_various.txt') is None:
        return

    portal = context.getSite()

    for user_data in TEST_USERS:
        username, password, group, portrait = (
            user_data.pop('username', None),
            user_data.pop('password', None),
            user_data.pop('group', None),
            user_data.pop('portrait', None)
        )
        if username not in portal.acl_users.getUserIds():
            try:
                portal.portal_registration.addMember(username, password)
                if group:
                    portal.portal_groups.addPrincipalToGroup(username, group)
                user = portal.portal_membership.getMemberById(username)
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
                    portal.portal_memberdata._setPortrait(
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


def set_operatives(item):
    from collective.simplemanagement.structures import Resource
    data = eval(item)

    def create_operative(val):
        res = Resource()
        res.role = val[0]
        res.user_id = unicodize(val[1])
        return res

    return [create_operative(i) for i in data]


def set_environments(item):
    from collective.simplemanagement.structures import Environment
    data = eval(item)

    def create_obj(val):
        res = Environment()
        res.name = val[0]
        res.env_type = val[1]
        res.url = val[2]

        return res

    return [create_obj(i) for i in data]


def set_milestones(item):
    from collective.simplemanagement.structures import Milestone
    data = eval(item)

    def create_obj(val):
        res = Milestone()
        res.name = val[0]
        res.status = val[1]

        return res

    return [create_obj(i) for i in data]


DATE_REGEX = re.compile(
    r'^(?P<sign>\+|-)(?P<value>[0-9]+)(?P<quantifier>[dw])$'
)


def convert_date(value):
    today = date.today()
    values = DATE_REGEX.match(value).groupdict()
    delta_value = int(values['value'])
    if values['quantifier'] == 'd':
        delta = timedelta(days=delta_value)
    elif values['quantifier'] == 'w':
        delta = timedelta(days=(delta_value*7))
    if values['sign'] == '+':
        return today + delta
    else:
        return today - delta
