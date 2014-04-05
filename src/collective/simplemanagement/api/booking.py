from datetime import date
from decimal import Decimal
from zope.component import getUtility

from z3c.relationfield.relation import create_relation

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from ..configure import Settings
from ..interfaces import IProject
from ..interfaces import IStory
from ..interfaces import IBookingStorage
from ..utils import quantize


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
                 date=None, project=None,
                 sort=True, **kwargs):
    """ returns bookings.
    ``owner`` limits results to objs belonging to that user.
    ``project`` project object or uid.
    ``references`` uid or list of uids to referenced objects.
    ``date`` datetime object or tuple of datetime objects to query a range.
    ``sort`` disable sorting.
    """
    query = {}
    if owner or kwargs.get('userid'):
        query['owner'] = owner or kwargs.get('userid')

    # get references
    references = references or []
    if project:
        if IProject.providedBy(project):
            project = project.UID()
        references.append(project)

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
