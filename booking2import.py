#-*- coding: utf-8 -*-

# ===============================================
# Script for importing bookings from json files
# exported using ``booking2export.py``.
# ===============================================

import transaction
import sys
import json
import time
import datetime

from zope.component.hooks import setSite

from collective.simplemanagement import api
from collective.simplemanagement.booking.storage import BookingStorage
from collective.simplemanagement.interfaces import IBookingStorage

try:
    site_id = sys.argv[3]
except:
    site_id = 'Plone'

try:
    fname = sys.argv[4]
except:
    fname = 'booking.json'

site = getattr(app, site_id)
# need to get the right site manager for `create_bookings`
setSite(site)

start = time.time()


def register_storage(site):
    sm = site.getSiteManager()
    utility = sm.queryUtility(IBookingStorage)
    if utility is None:
        utility = BookingStorage()
        sm.registerUtility(utility, IBookingStorage)
        transaction.commit()
        print 'REGISTERED UTILITY'


def convert_date(dt):
    dt = datetime.datetime.strptime(dt, '%a, %d %b %Y')
    return dt.date()


def import_bookings(bookings):
    for i, item in enumerate(bookings):
        print i
        item['date'] = convert_date(item['date'])
        api.booking.create_booking(**item)
        if not i % 1000:
            transaction.savepoint(optimistic=True)


register_storage(site)


bookings = []
with open(fname, 'r') as jsonfile:
    bookings = json.loads(jsonfile.read())

import_bookings(bookings)

stop = time.time()
transaction.commit()

print '### IMPORT BOOKING FINISHED ###'
print 'Took ', stop - start, 'seconds, aka ', (stop - start) / 60, 'minutes.'
print 'IMPORTED', len(bookings), 'bookings.'
