from datetime import date
from decimal import Decimal
from zope.component import getUtility

from z3c.relationfield.relation import create_relation

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from ..configure import Settings
from ..interfaces import IStory
from ..interfaces import IBookingStorage
from ..utils import AttrDict, quantize
from .date import datetimerange


def to_utf8(x):
    if isinstance(x, unicode):
        return x.encode('utf-8')
    return x


def to_references(x):
    return [(to_utf8(y[0]), to_utf8(y[1]))
            for y in x]


convert_funcs = {
    'owner': to_utf8,
    'text': safe_unicode,
    'references': to_references,
    'tags': lambda x: set([safe_unicode(y) for y in x]),
    'related': lambda x: create_relation('/'.join(x.getPhysicalPath()))
}


def get_booking_storage():
    return getUtility(IBookingStorage)


def create_booking(**values):
    """ create booking.
        `values` must contains booking params.
    """
    if not 'date' in values.keys():
        values['date'] = date.today()
    for k, v in values.iteritems():
        if v and k in convert_funcs:
            values[k] = convert_funcs[k](v)
    storage = get_booking_storage()
    return storage.create(**values)


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


def get_bookings(owner=None, references=None,
                 date=None, booking_date=None,
                 project=None,
                 sort=True, **kwargs):
    """ returns bookings.
    ``owner`` limits results to objs belonging to that user.
    ``references`` uid or list of uids to referenced objects.
    ``date`` datetime object or tuple of datetime objects to query a range.
    ``sort`` disable sorting.
    """
    query = {}
    if owner:
        query['owner'] = owner

    # get references
    references = references or []
    if references:
        if not isinstance(references, (list, tuple)):
            references = (references, )
        query['references'] = references

    if date:
        query['date'] = date

    dates = []
    for k in ('from_date', 'to_date'):
        dates.append(kwargs.get(k))
    if any(dates):
        query['date'] = tuple(dates)

    # sorting = None
    # if sort:
    #     sorting = {
    #         'sort_on': 'date',
    #         'sort_order': 'descending',
    #     }

    storage = get_booking_storage()
    return storage.query(query)


def get_booking_holes(owner, bookings, expected_working_time=None,
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
    holes = tuple(holes_utility.iter_user(owner, from_date, to_date))
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
