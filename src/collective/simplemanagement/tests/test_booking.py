from datetime import date
# from datetime import timedelta
# from decimal import Decimal

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


class TestBooking(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.project1 = self.portal['test-project']
        self.portal.invokeFactory('Project',
                                  'test-project-2',
                                  title=u"Test project 2")
        self.project2 = self.portal['test-project-2']
        login(self.portal, TEST_USER_NAME)
        # self.setup_bookings()
        self.bookings = []
        self.reset_storage()

    def tearDown(self):
        self.bookings = []
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        del self.portal[self.project1.id]
        del self.portal[self.project2.id]

    def reset_storage(self):
        util = getUtility(IBookingStorage)
        util.bookings.clear()
        util.mapping.clear()
        util.catalog.clear()

    def setup_bookings(self, dates, owner='', references=None, tags=None):
        for i, (dt, tm) in enumerate(dates):
            bdata = {
                'text': 'Booking %s %s' % (owner, i),
                'date': dt,
                'time': tm,
                'owner': owner,
                'references': references,
                'tags': tags,
            }
            bkng = api.booking.create_booking(**bdata)
            self.bookings.append(bkng)

    def test_get_storage(self):
        util = getUtility(IBookingStorage)
        self.assertTrue(verifyObject(IBookingStorage, util))

    def test_create_booking(self):
        values = {
            'text': 'Booking now!',
            'date': date(2014, 1, 1),
            'time': 2,
            'references': [
                # unicode string gets converted!
                (u'project', self.project1.UID()),
            ],
            'tags': set(sorted(['foo', 'bar', 'baz'])),
        }
        booking = api.booking.create_booking(**values)
        self.assertTrue(verifyObject(IBooking, booking))
        for k, v in values.iteritems():
            self.assertEqual(getattr(booking, k), v)
        # retrieve booking via storage
        storage = getUtility(IBookingStorage)
        self.assertTrue(booking.uid in storage)
        self.assertEqual(booking, storage[booking.uid])

    def test_get_bookings(self):
        dates = [
            # (date, worked hours)
            (date(2014, 1, 1), 4),
            (date(2014, 1, 2), 2),
            (date(2014, 1, 2), 3),
            (date(2014, 1, 3), 7),
            (date(2014, 1, 4), 3),
            (date(2014, 1, 4), 1),
            (date(2014, 1, 5), 2),
            (date(2014, 1, 5), 2),
        ]
        user1 = u'johndoe'
        user1_refs = [
            ('project', self.project1.UID()),
            ('story', self.project1['test-story-1'].UID()),
        ]
        user1_tags = ['boo', 'baz']
        user2 = u'popeye'
        user2_refs = [
            ('project', self.project1.UID()),
            ('story', self.project1['test-story-2'].UID()),
        ]
        user2_tags = ['foo', 'baz']
        user3 = 'goofy'
        user3_refs = [
            ('project', self.project2.UID()),
        ]
        user3_tags = ['boo', 'foo']
        self.setup_bookings(dates[:4], owner=user1,
                            references=user1_refs, tags=user1_tags)
        self.setup_bookings(dates[:2], owner=user2,
                            references=user2_refs, tags=user2_tags)
        self.setup_bookings(dates[2:5], owner=user3,
                            references=user3_refs, tags=user3_tags)

        bookings = api.booking.get_bookings()

        # total bookings
        self.assertEqual(len(bookings), 9)
        # user1 bookings
        u1_bookings = api.booking.get_bookings(owner=user1)
        self.assertEqual(len(u1_bookings), 4)
        # user2 bookings
        u2_bookings = api.booking.get_bookings(owner=user2)
        self.assertEqual(len(u2_bookings), 2)
        # user2 bookings
        u3_bookings = api.booking.get_bookings(owner=user3)
        self.assertEqual(len(u3_bookings), 3)

        # get booking by project
        # project 1
        p1_bookings = api.booking.get_bookings(references=self.project1.UID())
        self.assertEqual(len(p1_bookings), len(u1_bookings + u2_bookings))
        # project 2
        p2_bookings = api.booking.get_bookings(references=self.project2.UID())
        self.assertEqual(len(p2_bookings), len(u3_bookings))
        # all
        refs = [
            self.project1.UID(),
            self.project2.UID(),
        ]
        allp_bookings = api.booking.get_bookings(references=refs)
        self.assertEqual(len(allp_bookings), len(bookings))

        # by date
        _date = date(2014, 1, 1)
        expected = [x for x in self.bookings if x.date == _date]
        bookings = api.booking.get_bookings(date=_date)
        self.assertEqual(len(bookings), len(expected))
        _date = date(2014, 1, 2)
        expected = [x for x in self.bookings if x.date == _date]
        bookings = api.booking.get_bookings(date=_date)
        self.assertEqual(len(bookings), len(expected))
        dates = (date(2014, 1, 2), date(2014, 1, 5))
        bookings = api.booking.get_bookings(date=dates)
        expected = [x for x in self.bookings if x.date != date(2014, 1, 1)]
        self.assertEqual(len(bookings), len(expected))

        # TODO: test get bookings limited to specific refs such as projects

    # def test_missing_bookings(self):
    #     owner = TEST_USER_ID
    #     pc = self.portal.portal_catalog
    #     expected_working_time = 6
    #     man_day_hours = 8
    #     today = date(2014, 1, 5)
    #     from_date = today - timedelta(3)
    #     to_date = today - timedelta(1)

    #     bookings = api.booking.get_bookings(
    #         owner=owner,
    #         portal_catalog=pc,
    #         sort=False
    #     )
    #     # filtering catalog search using from/to date does not work in tests
    #     bookings = [x.getObject() for x in bookings
    #                 if from_date <= x.getObject().date <= to_date]
    #     holes = api.booking.get_booking_holes(
    #         owner, bookings,
    #         expected_working_time=expected_working_time,
    #         man_day_hours=man_day_hours,
    #         from_date=from_date,
    #         to_date=to_date
    #     )
    #     expected = 3  # we expect also entire missing day
    #     assert len(holes) == expected, \
    #         'found %s holes instead of %s' % (len(holes), expected)
    #     # now we can create a hole for one of the missing booking
    #     # on 2014/1/4 we worked 4 hours so we create a hole
    #     # for the remaing 4 hours
    #     utility = getUtility(IBookingHoles)
    #     hole = BookingHole(
    #         date(2014, 1, 4),
    #         Decimal("4"),
    #         owner,
    #         reason=u"sick"
    #     )
    #     utility.add(hole)
    #     # now we expect to have 1 missing booking less
    #     holes = api.booking.get_booking_holes(
    #         owner, bookings,
    #         expected_working_time=expected_working_time,
    #         man_day_hours=man_day_hours,
    #         from_date=from_date,
    #         to_date=to_date)
    #     expected = 2
    #     assert len(holes) == expected, \
    #             'found %s holes instead of %s' % (len(holes), expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBooking))
    return suite
