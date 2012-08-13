from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
# TODO: harmonize differences display and warning display
from .configure import WARNING_DELTA, WARNING_DELTA_PERCENT


def get_timings(context, portal_catalog=None):
    # TODO: this can be slow: see if it can be asyncronous (via javascript)
    if portal_catalog is None:
        pc = getToolByName(context, 'portal_catalog')
    else:
        pc = portal_catalog
    if IStory.providedBy(context):
        estimate = context.estimate
    else:
        stories = pc.searchResults({
            'path': '/'.join(context.getPhysicalPath()),
            'portal_type': 'Story'
        })
        estimate = sum([ s.estimate for s in stories ])
    bookings = pc.searchResults({
        'path': '/'.join(context.getPhysicalPath()),
        'portal_type': 'Booking'
    })
    hours = sum([ b.time for b in bookings ])
    # TODO: the delta should be a percentage and probably differentiate more
    difference = estimate - hours
    difference_status = 'success'
    if difference < 0:
        difference_status = 'danger'
    if difference > WARNING_DELTA:
        difference_status = 'warning'
    return {
        'estimate': estimate,
        'resource_time': hours,
        'difference': difference,
        'status': difference_status
    }


def get_difference_class(a, b):
    if (abs(float(a - b)) / float(max(a, b))) > WARNING_DELTA_PERCENT:
        return 'danger'
    return 'success'


def get_user_details(context, user_id):
    pm = getToolByName(context, 'portal_membership')
    usr = pm.getMemberById(user_id)
    return {
        'fullname': usr.getProperty('fullname') or user_id,
        'href': '/author/%s' % user_id  # TODO: fix with the right url
    }
