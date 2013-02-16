from copy import copy
from decimal import Decimal
from datetime import date, time, datetime

from zope.component import getUtility
from zope.component.hooks import getSite
from zope.location.interfaces import ILocation

from Products.CMFCore.utils import getToolByName

from collective.prettydate.interfaces import IPrettyDate

from .interfaces import IStory
from .interfaces import IProject
from .interfaces import IIteration
from .interfaces import IBookingHoles
from .configure import Settings, DECIMAL_QUANT


def quantize(value):
    return value.quantize(DECIMAL_QUANT)


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


def get_story(context, default=None):
    return get_ancestor(IStory, context, default)


def get_project(context, default=None):
    return get_ancestor(IProject, context, default)


def get_iteration(context, default=None):
    return get_ancestor(IIteration, context, default)


def get_bookings(userid=None, project=None, portal_catalog=None,
                 from_date=None, to_date=None, sort=True):
    """ returns bookings.
    ``userid`` limits results to objs belonging to that user.
    ``project`` a project obj. If given, results will be limited to that proj.
    ``from_date`` lower date limit
    ``to_date`` upper date limit
    ``sort`` disable sorting
    """
    if portal_catalog is None:
        pc = getToolByName(getSite(), 'portal_catalog')
    else:
        pc = portal_catalog
    query = {
        'portal_type': 'Booking',
    }
    if sort:
        # this is not working in tests (???)
        query['sort_on'] = 'booking_date'
    if userid:
        query['Creator'] = userid
    if project:
        query['path'] = '/'.join(project.getPhysicalPath())
    if from_date and not to_date:
        query['booking_date'] = {'query': from_date, 'range': 'min'}
    elif to_date and not from_date:
        query['booking_date'] = {'query': to_date, 'range': 'max'}
    elif from_date and to_date:
        query['booking_date'] = {'query': [from_date, to_date], 'range': 'minmax'}
    return pc.searchResults(query)


def get_booking_holes(userid, bookings, expected_working_time=None,
                      man_day_hours=None, from_date=None, to_date=None):
    # TODO: get settings from global settings if not passed
    _missing = {}
    for booking in bookings:
        if booking.time >= expected_working_time:
            # let's skip this if already have sufficient hours
            continue
        # let's check for a hole matching this booking
        if _missing.get(booking.date):
            _missing[booking.date] += booking.time
        else:
            _missing[booking.date] = booking.time

    # then we check that total time matches our constraints
    holes_utility = getUtility(IBookingHoles)
    holes = tuple(holes_utility.iter_user(userid,
                                       from_date,
                                       to_date))
    missing = []
    for dt, tm in sorted(_missing.items()):
        if tm >= expected_working_time:
            # drop it if time is enough
            continue
        the_hole = [x for x in holes if dt == x.day]
        if the_hole and \
            (the_hole[0].hours + tm) >= expected_working_time:
            # if we have a hole matching our booking date
            # and hole hours + booked time matches our constraint
            # we are ok with this booking
            continue
        missing.append(AttrDict({
            # 'date': plone_view.toLocalizedTime(booking.date),
            'date': dt,
            'time': tm,
        }))
    return missing


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
        estimate = sum([s.estimate for s in stories], Decimal("0.00"))
    bookings = pc.searchResults({
        'path': '/'.join(context.getPhysicalPath()),
        'portal_type': 'Booking'
    })
    hours = sum([b.time for b in bookings if b.time], Decimal("0.00"))
    difference = estimate - hours
    return {
        'estimate': quantize(estimate),
        'resource_time': quantize(hours),
        'difference': quantize(difference),
        'time_status': get_difference_class(estimate, hours)
    }


def get_difference_class(a, b, settings=None):
    if a > 0 or a < 0:
        if settings is None:
            settings = Settings()
        difference = a - b
        if (abs(difference) / a) > settings.warning_delta_percent:
            if difference < 0:
                return 'danger'
            else:
                return 'warning'
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
    assignees = getattr(story, 'assigned_to') or []
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
        current = copy(self.current)
        next = current + self.step
        self.current = next
        return (current, next)


def timeago(timestamp, short=False):
    utility = getUtility(IPrettyDate)
    if isinstance(timestamp, date):
        return utility.date(
            datetime.combine(timestamp, time(0, 0)),
            short=short,
            asdays=True
        )
    elif isinstance(timestamp, datetime):
        return utility.date(timestamp, short=short)
    raise ValueError(
        "'%s' cannot be converted prettily" % type(timestamp).__name__
    )


class AttrDict(dict):
    """ a smarter dict
    """

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v
