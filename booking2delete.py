#-*- coding: utf-8 -*-

# ====================================================================
# Script for TESTING PURPOSE that deletes N bookings from plone site
# to allow to test export/import with less objects.
# ====================================================================


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


import time as builtin_time

import transaction
import plone.api



FNAME = 'booking.json'

start = builtin_time.time()


def delete_bookings(site):
    """ export bookings to json file
    """
    catalog = site.portal_catalog

    all_bookings = catalog(portal_type='Booking')[2000:7000]

    for i, brain in enumerate(all_bookings):
        try:
            obj = brain.getObject()
            print 'Deleting', brain.getPath()
            plone.api.content.delete(obj)
        except:
            print 'ERROR', brain.getPath()

    print 'deleted', len(all_bookings)


delete_bookings(site)

stop = builtin_time.time()


print 'Deleted'
transaction.commit()
