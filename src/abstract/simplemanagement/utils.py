from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
from .configure import WARNING_DELTA


def get_timings(context, portal_catalog=None):
    # TODO: this can be slow: see if it can be asyncronous (via javascript)
    if portal_catalog is None:
        pc = getToolByName(context, 'portal_catalog')
    else:
        pc = portal_catalog
    if IStory.providedBy(context):
        estimate = context.estimate
    else:
        estimate = 0
        stories = pc.searchResults({
            'path': '/'.join(context.getPhysicalPath()),
            'portal_type': 'Story'
        })
        for story in stories:
            estimate += story.estimate
    hours = 0
    bookings = pc.searchResults({
        'path': '/'.join(context.getPhysicalPath()),
        'portal_type': 'Booking'
    })
    for booking in bookings:
        hours += booking.time
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
