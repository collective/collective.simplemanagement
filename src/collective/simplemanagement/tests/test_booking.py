from datetime import date
from datetime import timedelta
from decimal import Decimal

import unittest2 as unittest
from zope.component import getUtility
from zope.interface.verify import verifyObject

from plone.app.testing import (TEST_USER_ID,
                               TEST_USER_NAME,
                               login,
                               setRoles)

from ..testing import BASE_INTEGRATION_TESTING
from ..interfaces import IBooking
from ..interfaces import IBookingStorage
from .. import api


class TestBookingCheck(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.project1 = self.portal['test-project']
        # self.portal.invokeFactory('Project',
        #                           'test-project-2',
        #                           title=u"Test project 2")
        # self.project2 = self.portal['test-project-2']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        # self.setup_bookings()

    def tearDown(self):
        self.remove_bookings()
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def get_story(self):
        # stories have been already setup by layer conf
        brains = self.portal.portal_catalog(portal_type='Story')
        return brains[0].getObject()

    def setup_bookings(self, userid=''):
        story = self.get_story()
        self.booking_data = [
            # (date, worked hours)
            (date(2013, 1, 1), 4),
            (date(2013, 1, 2), 2),
            (date(2013, 1, 2), 3),
            (date(2013, 1, 3), 7),
            (date(2013, 1, 4), 3),
            (date(2013, 1, 4), 1),
            (date(2013, 1, 5), 2),
            (date(2013, 1, 5), 2),
        ]
        if not hasattr(self, 'bookings'):
            self.bookings = []
        for i, (dt, tm) in enumerate(self.booking_data):
            bkng = api.booking.create_booking(
                story,
                {
                    'title': 'Booking %s %s' % (userid, i),
                    'date': dt,
                    'time': tm,
                }
            )
            if userid:
                bkng.setCreators((userid))
                bkng.reindexObject()
            self.bookings.append(bkng)

    def remove_bookings(self):
        pass

    def test_get_storage(self):
        util = getUtility(IBookingStorage)
        self.assertTrue(verifyObject(IBookingStorage, util))

    # def test_get_bookings(self):
    #     self.setup_bookings(userid='johndoe')
    #     pc = self.portal.portal_catalog
    #     # every user should have 6 bookings
    #     bookings = api.booking.get_bookings(
    #         userid=TEST_USER_ID,
    #         portal_catalog=pc,
    #         sort=False
    #     )
    #     assert len(bookings) == 8
    #     bookings = api.booking.get_bookings(
    #         userid='johndoe',
    #         portal_catalog=pc,
    #         sort=False
    #     )
    #     assert len(bookings) == 8
    #     # if no user passed we shold get all the bookings
    #     bookings = api.booking.get_bookings(
    #         portal_catalog=pc,
    #         sort=False
    #     )
    #     assert len(bookings) == 16
    #     # TODO: test get bookings limited to projects

    # def test_missing_bookings(self):
    #     userid = TEST_USER_ID
    #     pc = self.portal.portal_catalog
    #     expected_working_time = 6
    #     man_day_hours = 8
    #     today = date(2013, 1, 5)
    #     from_date = today - timedelta(3)
    #     to_date = today - timedelta(1)

    #     bookings = api.booking.get_bookings(
    #         userid=userid,
    #         portal_catalog=pc,
    #         sort=False
    #     )
    #     # filtering catalog search using from/to date does not work in tests
    #     bookings = [x.getObject() for x in bookings
    #                 if from_date <= x.getObject().date <= to_date]
    #     holes = api.booking.get_booking_holes(
    #         userid, bookings,
    #         expected_working_time=expected_working_time,
    #         man_day_hours=man_day_hours,
    #         from_date=from_date,
    #         to_date=to_date
    #     )
    #     expected = 3  # we expect also entire missing day
    #     assert len(holes) == expected, \
    #         'found %s holes instead of %s' % (len(holes), expected)
    #     # now we can create a hole for one of the missing booking
    #     # on 2013/1/4 we worked 4 hours so we create a hole
    #     # for the remaing 4 hours
    #     utility = getUtility(IBookingHoles)
    #     hole = BookingHole(
    #         date(2013, 1, 4),
    #         Decimal("4"),
    #         userid,
    #         reason=u"sick"
    #     )
    #     utility.add(hole)
    #     # now we expect to have 1 missing booking less
    #     holes = api.booking.get_booking_holes(
    #         userid, bookings,
    #         expected_working_time=expected_working_time,
    #         man_day_hours=man_day_hours,
    #         from_date=from_date,
    #         to_date=to_date)
    #     expected = 2
    #     assert len(holes) == expected, \
    #             'found %s holes instead of %s' % (len(holes), expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBookingCheck))
    return suite
