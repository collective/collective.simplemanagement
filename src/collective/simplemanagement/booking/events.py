#-*- coding: utf-8 -*-

from zope.interface import implements
from zope.component.interfaces import IObjectEvent


class IBookingAddedEvent(IObjectEvent):
    """ An event signaling that a booking has been created
    """


class BookingAddedEvent(object):
    implements(IBookingAddedEvent)

    def __init__(self, ob):
        self.object = ob
        self.booking = ob
