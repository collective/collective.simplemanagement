#-*- coding: utf-8 -*-

# ===============================================
# Script for reindexing all bookings.
# You may run this if you encounter conflicts
# with catalog ids.
# ===============================================

import transaction
import sys
import time

from zope.component.hooks import setSite

from collective.simplemanagement.interfaces import IBookingStorage

try:
    site_id = sys.argv[3]
except:
    site_id = 'Plone'

site = getattr(app, site_id)
# need to get the right site manager for `create_bookings`
setSite(site)

start = time.time()

def get_utility(site):
    sm = site.getSiteManager()
    return sm.queryUtility(IBookingStorage)

storage = get_utility(site)
storage.reindex_catalog()
transaction.commit()
stop = time.time()

print '### REINDEX BOOKING CATALOG FINISHED ###'
print 'Took ', stop - start, 'seconds, aka ', (stop - start) / 60, 'minutes.'
