import re
from datetime import date, timedelta

import pkg_resources
from Products.CMFPlone.utils import getToolByName

try:
    pkg_resources.get_distribution('collective.transmogrifier')
except pkg_resources.DistributionNotFound:
    HAS_TRANSMOGRIFIER = False
else:
    from collective.transmogrifier.transmogrifier import Transmogrifier
    HAS_TRANSMOGRIFIER = True


def create_users(context):
    if context.readDataFile('loadcontent_various.txt') is None:
        return

    portal = context.getSite()
    test_users = [
        ('employee1', 'employee1', 'employees'),
        ('employee2', 'employee2', 'employees'),
        ('pm1', 'pm1', 'PM'),
        ('customer', 'customer', None),
    ]

    for username, password, group in test_users:
        if username not in portal.acl_users.getUserIds():
            try:
                portal.portal_registration.addMember(username, password)
                if group:
                    portal.portal_groups.addPrincipalToGroup(username, group)
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
        res.user_id = val[1]
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
