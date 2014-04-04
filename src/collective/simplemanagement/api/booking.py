from datetime import date
from decimal import Decimal
from zope.component import getUtility
from zope.component.hooks import getSite

from z3c.relationfield.relation import create_relation
from plone.dexterity.utils import createContentInContainer

from Products.CMFCore.utils import getToolByName

from ..configure import Settings
from ..configure import DECIMAL_QUANT
from ..interfaces import IStory
from ..utils import AttrDict, quantize
from .date import datetimerange


convert_funcs = {
    'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
}


def create_booking(context, data, reindex=True):
    """ create booking in given `context`.
        `data` must contains booking params.
        `reindex` switches on/off new item reindexing.
    """
    assert 'title' in data.keys()
    item = createContentInContainer(
        context,
        'Booking',
        title=data.pop('title')
    )
    if not 'date' in data.keys():
        data['date'] = date.today()
    for k, v in data.items():
        if v and k in convert_funcs:
            v = convert_funcs[k](v)
        setattr(item, k, v)
    if reindex:
        item.reindexObject()
    return item


def create_hole(day, hours, user_id, reason=""):
    # hole = BookingHole(day, hours, user_id, reason)
    # util = getUtility(IBookingHoles)
    # util.add(hole)
    # return hole
    print 'nothing to do here buddy!'


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


def get_bookings(userid=None, project=None, portal_catalog=None,
                 from_date=None, to_date=None, booking_date=None,
                 sort=True):
    """ returns bookings.
    ``userid`` limits results to objs belonging to that user.
    ``project`` a project obj. If given, results will be limited to that proj.
    ``from_date`` lower date limit
    ``to_date`` upper date limit
    ``sort`` disable sorting
    """
    if portal_catalog is None:
        context = project or getSite()
        pc = getToolByName(context, 'portal_catalog')
    else:
        pc = portal_catalog
    query = {
        'portal_type': 'Booking',
    }
    if userid:
        query['Creator'] = userid
    if project:
        query['path'] = '/'.join(project.getPhysicalPath())
    if from_date and not to_date:
        query['booking_date'] = {'query': from_date, 'range': 'min'}
    elif to_date and not from_date:
        query['booking_date'] = {'query': to_date, 'range': 'max'}
    elif from_date and to_date:
        query['booking_date'] = {'query': [from_date, to_date],
                                 'range': 'min:max'}
    if booking_date:
        query['booking_date'] = booking_date
    if sort:
        # XXX: this is not working in tests (???)
        query['sort_on'] = 'booking_date'
        query['sort_order'] = 'descending'

    return pc.searchResults(query)


def get_booking_holes(userid, bookings, expected_working_time=None,
                      man_day_hours=None, from_date=None, to_date=None):
    """ given a user and a list of bookings returns booking holes
    ``expected_working_time`` minimal expected working hours per day
    ``man_day_hours`` amount of working hours per day
    ``from_date`` and ``to_date`` limit the range of dates to check upon
    """
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

    # look up for entire-day hole
    for adate, __ in datetimerange(from_date, to_date, exclude_weekend=1):
        if not adate in _missing:
            _missing[adate] = Decimal('0.0')

    # then we check that total time matches our constraints
    holes_utility = getUtility(IBookingHoles)
    holes = tuple(holes_utility.iter_user(userid, from_date, to_date))
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
    bookings = get_bookings(project=context)
    hours = sum([b.time for b in bookings if b.time], Decimal("0.00"))
    difference = estimate - hours
    return {
        'estimate': quantize(estimate),
        'resource_time': quantize(hours),
        'difference': quantize(difference),
        'time_status': get_difference_class(estimate, hours)
    }
