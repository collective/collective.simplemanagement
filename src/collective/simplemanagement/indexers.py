from DateTime import DateTime
from plone.indexer.decorator import indexer

from .interfaces import IIteration
from .interfaces import IBooking


@indexer(IIteration)
def start(obj):
    return DateTime(obj.start.isoformat())


@indexer(IIteration)
def end(obj):
    return DateTime(obj.end.isoformat())


@indexer(IBooking)
def date(obj):
    return DateTime(obj.date.isoformat())
