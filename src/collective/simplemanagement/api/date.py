from copy import copy
from datetime import time
from datetime import datetime
from datetime import date
from DateTime import DateTime

from zope.component import getUtility

from plone import api
from collective.prettydate.interfaces import IPrettyDate

from ..configure import ONE_DAY


class datetimerange(object):
    """Just like ``xrange``, but working on ``datetime``.
    """

    weekend_days = (5, 6)

    def __init__(self, from_, to, step=ONE_DAY, exclude_weekend=False):
        self.from_ = from_
        self.current = from_
        self.limit = to
        self.step = step
        self.exclude_weekend = exclude_weekend

    def __iter__(self):
        return self.__class__(
            self.from_,
            self.limit,
            self.step,
            exclude_weekend=self.exclude_weekend,
        )

    def next(self):
        if self.current >= self.limit:
            raise StopIteration()
        current = copy(self.current)
        next = current + self.step
        if self.exclude_weekend:
            while current.weekday() in self.weekend_days:
                current += self.step
                next += self.step
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


def format(timestamp, long=False):
    if isinstance(timestamp, date):
        timestamp = DateTime(datetime.combine(timestamp, time(0, 0)))
    elif isinstance(timestamp, datetime):
        timestamp = DateTime(timestamp)
    return api.portal.get_localized_time(
        datetime=timestamp,
        long_format=long
    )
