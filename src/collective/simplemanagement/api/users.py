from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from ..configure import Settings
from ..utils import AttrDict


def get_user_details(context, user_id, **kwargs):
    pm = kwargs.get(
        'portal_membership',
        getToolByName(context, 'portal_membership')
    )
    portal_url = kwargs.get(
        'portal_url',
        getToolByName(context, 'portal_url')
    )
    usr = pm.getMemberById(user_id)
    data = AttrDict({
        'user_id': user_id,
        'fullname': user_id,
        'href': None,
        'portrait': None
    })
    if usr:
        data['fullname'] = usr.getProperty('fullname') or user_id
        data['href'] = "%s/dashboard?employee=%s" % (portal_url(), user_id)
        data['portrait'] = pm.getPersonalPortrait(user_id)
        if data['portrait'] is not None:
            data['portrait'] = data['portrait'].absolute_url()
    return data


def get_assignees_details(story):
    assignees = getattr(story, 'assigned_to') or []
    for user_id in assignees:
        yield get_user_details(story, user_id)


def get_employee_ids(context=None):
    settings = Settings()
    resources = ['admin']  # BBB: this needs to be extracted someway!
    if not context:
        context = getSite()
    gtool = getToolByName(context, 'portal_groups')
    group = gtool.getGroupById(
        settings.employees_group
    )
    if group is not None:
        resources.extend(group.getMemberIds())
    return resources
