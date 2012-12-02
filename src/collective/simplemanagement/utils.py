from zope.location.interfaces import ILocation
from Products.CMFCore.utils import getToolByName

from .interfaces import IStory, IProject
# TODO: harmonize differences display and warning display
# Also move config into p.a.registry
from .configure import WARNING_DELTA, WARNING_DELTA_PERCENT


def boolize(value):
    if value.lower() in ('1', 'on', 'true'):
        return True
    return False


def get_project(context, default=None):
    current = context
    while ILocation.providedBy(current) and current.__parent__ is not None:
        if IProject.providedBy(current):
            return current
        current = current.__parent__
    return default


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
    # TODO: also obtain image
    pm = getToolByName(context, 'portal_membership')
    usr = pm.getMemberById(user_id)
    if usr:
        fullname = usr.getProperty('fullname') or user_id
        href = '/author/%s' % user_id  # TODO: fix with the right url
    else:
        fullname = user_id
        href = None
    return dict(fullname=fullname, href=href)


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


def get_text(context, text,
    source_mimetype='text/x-web-markdown', target_mimetype=None):
    """return the body text of an item
    """
    transforms = getToolByName(context, 'portal_transforms')

    if target_mimetype is None:
        target_mimetype = 'text/x-html-safe'

    if text is None:
        return ''

    if isinstance(text, unicode):
        text = text.encode('utf8')
    return transforms.convertTo(target_mimetype,
                                text,
                                context=context,
                                mimetype=source_mimetype).getData()


class datetimerange(object):
    """Just like ``xrange``, but working on ``datetime``.
    """

    def __init__(self, from_, to, step):
        self.from_ = from_
        self.current = from_
        self.limit = to
        self.step = step

    def __iter__(self):
        return self.__class__(
            self.from_,
            self.limit,
            self.step
        )

    def next(self):
        if self.current >= self.limit:
            raise StopIteration()
        current = self.current
        self.current = self.current + self.step
        return current
