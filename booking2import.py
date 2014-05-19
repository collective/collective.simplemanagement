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
import decimal

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

def ___wipe(site):
    """
    Wipes sites bookings.
    Use this
    (via pdb in this script for instance)
    if you need to drop all bookings
    to start with a fresh new import.
    **************************************
    ***** USE THIS AT YOUR OWN RISK! *****
    **************************************
    """
    util = get_utility(site)
    util.bookings.clear()
    util.mapping.clear()
    util.catalog.clear()
    print '*** BOOKING STORAGE WIPED OUT! ***'


def get_utility(site):
    sm = site.getSiteManager()
    return sm.queryUtility(IBookingStorage)


def register_storage(site):
    utility = get_utility(site)
    if utility is None:
        utility = BookingStorage()
        sm = site.getSiteManager()
        sm.registerUtility(utility, IBookingStorage)
        transaction.commit()
        print 'REGISTERED UTILITY'


def convert_date(dt):
    dt = datetime.datetime.strptime(dt, '%a, %d %b %Y')
    return dt.date()


def import_bookings(bookings):
    total = len(bookings)
    for i, item in enumerate(bookings):
        print i, '/', total
        item['date'] = convert_date(item['date'])
        api.booking.create_booking(**item)
        if not i % 1000:
            transaction.savepoint(optimistic=True)

register_storage(site)

bookings = []
with open(fname, 'r') as jsonfile:
    bookings = json.loads(jsonfile.read(), parse_float=decimal.Decimal)

import_bookings(bookings)

transaction.commit()
stop = time.time()

print '### IMPORT BOOKING FINISHED ###'
print 'Took ', stop - start, 'seconds, aka ', (stop - start) / 60, 'minutes.'
print 'IMPORTED', len(bookings), 'bookings.'
