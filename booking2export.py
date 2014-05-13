#-*- coding: utf-8 -*-

# ===============================================
# Script for exporting bookings to json file
# name `bookings.json`
# ===============================================

import sys
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Testing.makerequest import makerequest
from Products.CMFCore.tests.base.security import (PermissiveSecurityPolicy,
                                                  OmnipotentUser)

from zope.component.hooks import setSite

def spoofRequest(app):
    """
    Make REQUEST variable to be available on the Zope application server.

    This allows acquisition to work properly
    """
    _policy = PermissiveSecurityPolicy()
    _oldpolicy = setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))
    return makerequest(app)

# Enable Faux HTTP request object
app = spoofRequest(app)


try:
    site_id = sys.argv[3]
except:
    site_id = 'Plone'

site = getattr(app, site_id)
setSite(site)


import json
from decimal import Decimal
from datetime import time
from datetime import date
from datetime import datetime
from DateTime import DateTime


class ExtendedJSONEncoder(json.JSONEncoder):

    DATE_RFC822_FORMAT = '%a, %d %b %Y'
    TIME_RFC822_FORMAT = '%H:%M:%S'

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, DateTime):
            return obj.rfc822()
        elif isinstance(obj, date):
            return obj.strftime(self.DATE_RFC822_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(self.TIME_RFC822_FORMAT)
        elif isinstance(obj, datetime):
            return obj.strftime(
                self.DATE_RFC822_FORMAT + ' ' + self.TIME_RFC822_FORMAT + ' %z'
            )
        elif isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


import time as builtin_time

import transaction
import plone.api

from collective.simplemanagement import api
from collective.simplemanagement.interfaces import IBookingHoles


FNAME = 'booking.json'

start = builtin_time.time()


def remove_utility(site):
    """Removes the registered booking holes utility
    """
    sm = site.getSiteManager()
    sm.unregisterUtility(provided=IBookingHoles)
    return True


def export_bookings(site):
    """ export bookings to json file
    """
    tojson = []
    catalog = site.portal_catalog

    all_bookings = catalog(portal_type='Booking')
    total = len(all_bookings)
    print 'FOUND', total, 'bookings'
    print 'EXPORTED STARTED'

    for i, brain in enumerate(all_bookings):
        print i + 1, '/', total, ') PROCESSING:', brain.getPath()
        obj = brain.getObject()

        proj = api.content.get_project(obj)
        story = api.content.get_story(obj)

        text = ' '.join([
            '@' + proj.getId(),
            '@' + story.getId(),
            brain.Title.strip(),
        ])
        if brain.Description:
            text += ' > ' + ' '.join(brain.Description.splitlines())
        item = {
            'owner': brain.Creator,
            'date': brain.date,
            'text': text,
            'time': brain.time,
            'tags': brain.Subject and list(set(brain.Subject)) or []
        }
        # get references

        # We use the portal type, so it needs to be capitalized.
        references = [
            ('Project', proj.UID()),
            ('Story', story.UID()),
        ]
        item['references'] = references
        if obj.getRelatedItems():
            import pdb;pdb.set_trace()

        try:
            json.dumps(tojson, cls=ExtendedJSONEncoder)
        except Exception, e:
            print str(e)
            import pdb;pdb.set_trace()

        tojson.append(item)

        # delete and unindex
        plone.api.content.delete(obj)

        if not i % 1000:
            transaction.savepoint(optimistic=True)

    return tojson

bookings = export_bookings(site)

with open(FNAME, 'w') as output:
    output.write(json.dumps(bookings, cls=ExtendedJSONEncoder))

print 'REBUILDING CATALOG...'
site.portal_catalog.clearFindAndRebuild()
print 'CATALOG REBUILD DONE'

remove_utility(site)

transaction.commit()
stop = builtin_time.time()

print '### EXPORT BOOKING FINISHED ###'
print 'Took ', stop - start, 'seconds, aka ', (stop - start) / 60, 'minutes.'
print 'EXPORTED to "', FNAME, '" and DELETED', len(bookings), 'bookings.'
