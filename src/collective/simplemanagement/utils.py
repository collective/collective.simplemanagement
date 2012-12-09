from zope.location.interfaces import ILocation
from Products.CMFCore.utils import getToolByName

from .interfaces import IStory
from .interfaces import IProject
from .interfaces import IIteration
from .configure import Settings


def boolize(value):
    if value.lower() in ('1', 'on', 'true'):
        return True
    return False


def get_ancestor(iface, context, default=None):
    """Gets the ancestor of ``context`` providing ``iface``.

    Returns ``default`` if not found.
    """
    current = context
    while current is not None:
        if iface.providedBy(current):
            return current
        if not ILocation.providedBy(current):
            return default
        current = current.__parent__
    return default


def get_project(context, default=None):
    return get_ancestor(IProject, context, default)


def get_iteration(context, default=None):
    return get_ancestor(IIteration, context, default)


def get_timing_status(difference, settings=None):
    if settings is None:
        settings = Settings()
    # TODO: the delta should be a percentage and probably differentiate more
    difference_status = 'success'
    if difference < 0:
        difference_status = 'danger'
    if difference > settings.warning_delta:
        difference_status = 'warning'
    return difference_status


def get_timings(context, portal_catalog=None):
    # TODO: this probably breaks with the presence of estimate
    # in Iteration too, and the fact that everywhere is a decimal.
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


def get_difference_class(a, b, settings=None):
    if settings is None:
        settings = Settings()
    if (abs(a - b) / max(a, b)) > settings.warning_delta_percent:
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
