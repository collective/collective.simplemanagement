from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
# TODO: harmonize differences display and warning display
from .configure import WARNING_DELTA, WARNING_DELTA_PERCENT


def get_timing_status(difference):
    # TODO: the delta should be a percentage and probably differentiate more
    difference_status = 'success'
    if difference < 0:
        difference_status = 'danger'
    if difference > WARNING_DELTA:
        difference_status = 'warning'
    return difference_status


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
        estimate = sum([s.estimate for s in stories])
    bookings = pc.searchResults({
        'path': '/'.join(context.getPhysicalPath()),
        'portal_type': 'Booking'
    })
    hours = sum([b.time for b in bookings])
    difference = estimate - hours
    return {
        'estimate': estimate,
        'resource_time': hours,
        'difference': difference,
        'time_status': get_timing_status(difference)
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


def get_assignees_details(story):
    assignees = getattr(story, 'assigned_to')
    for user_id in assignees:
        yield get_user_details(story, user_id)


def get_epic_by_story(story):
    epic = None
    if story.epic and not story.epic.isBroken():
        epic = {
            'url': story.epic.to_object.absolute_url(),
            'title': story.epic.to_object.title
        }
    return epic
