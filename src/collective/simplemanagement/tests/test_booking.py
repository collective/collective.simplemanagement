from datetime import date
# from datetime import timedelta
# from decimal import Decimal

import unittest2 as unittest
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
        for i in xrange(1, 4):
            self.project1.invokeFactory('Story', 'story-%d' % i,
                                        title=(u"Test story %d" % i))
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
        util = api.booking.get_storage()
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
        util = api.booking.get_storage()
        self.assertTrue(verifyObject(IBookingStorage, util))

    def test_create_booking(self):
        values = {
            'text': 'Booking now!',
            'date': date(2014, 1, 1),
            'time': 2,
            'references': [
                # unicode string gets converted!
                (u'Project', self.project1.UID()),
            ],
            'tags': set(sorted(['foo', 'bar', 'baz'])),
        }
        booking = api.booking.create_booking(**values)
        self.assertTrue(verifyObject(IBooking, booking))
        for k, v in values.iteritems():
            self.assertEqual(getattr(booking, k), v)
        # retrieve booking via storage
        storage = api.booking.get_storage()
        self.assertTrue(booking.uid in storage)
        self.assertEqual(booking, storage[booking.uid])

        # default for project
        values = {
            'text': 'Booking now!',
            'time': 2,
            'references': [
                # unicode string gets converted!
                (u'Story', self.project1['story-1'].UID()),
            ],
        }
        booking = api.booking.create_booking(**values)
        self.assertEqual(booking.references_dict['Project'],
                         self.project1.UID())
        self.assertTrue(isinstance(booking.date, date))

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
            ('Project', self.project1.UID()),
            ('Story', self.project1['test-story-1'].UID()),
        ]
        user1_tags = ['boo', 'baz']
        user2 = u'popeye'
        user2_refs = [
            ('Project', self.project1.UID()),
            ('Story', self.project1['test-story-2'].UID()),
        ]
        user2_tags = ['foo', 'baz']
        user3 = 'goofy'
        user3_refs = [
            ('Project', self.project2.UID()),
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
        # project 1 (we can query via project object)
        p1_bookings = api.booking.get_bookings(project=self.project1)
        self.assertEqual(len(p1_bookings), len(u1_bookings) + len(u2_bookings))
        # project 2 (we can query via project UID)
        p2_bookings = api.booking.get_bookings(project=self.project2.UID())
        self.assertEqual(len(p2_bookings), len(u3_bookings))
        # all
        refs = [
            self.project1.UID(),
            self.project2.UID(),
        ]
        # project 1 + 2 (we can query via references)
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
        # BBB `from_date` and `to_date` support
        bookings = api.booking.get_bookings(from_date=dates[0],
                                            to_date=dates[1])
        expected = [x for x in self.bookings if x.date != date(2014, 1, 1)]
        self.assertEqual(len(bookings), len(expected))

        bookings = api.booking.get_bookings(from_date=dates[0])
        expected = [x for x in self.bookings if x.date >= dates[0]]
        self.assertEqual(len(bookings), len(expected))

        bookings = api.booking.get_bookings(to_date=dates[0])
        expected = [x for x in self.bookings if x.date <= dates[0]]
        self.assertEqual(len(bookings), len(expected))

        # test sorting
        # we sort on reverse date by default (only sorting index ATM)
        bookings = api.booking.get_bookings()
        first_date = date(2014, 1, 4)
        last_date = date(2014, 1, 1)
        self.assertEqual(bookings[0].date, first_date)
        self.assertEqual(bookings[-1].date, last_date)
        # reverse (normal date sorting)
        bookings = api.booking.get_bookings(reverse=False)
        first_date = date(2014, 1, 1)
        last_date = date(2014, 1, 4)
        self.assertEqual(bookings[0].date, first_date)
        self.assertEqual(bookings[-1].date, last_date)

    def test_storage(self):
        dates = [
            # (date, worked hours)
            (date(2014, 1, 1), 4),
            (date(2014, 1, 2), 2),
            (date(2014, 1, 3), 3),
            (date(2014, 1, 4), 7),
            (date(2014, 1, 5), 3),
            (date(2014, 1, 6), 1),
            (date(2014, 1, 7), 2),
            (date(2014, 1, 8), 2),
        ]
        self.setup_bookings(
            dates,
            owner='johndoe',
            references=('Project', self.project2.UID()),
            tags=['foo', 'bar']
        )
        storage = api.booking.get_storage()
        all_ = storage.query(None)
        self.assertEqual(len(all_), 8)
        self.assertEqual(
            [ i.date.day for i in all_ ],
            [1, 2, 3, 4, 5, 6, 7, 8]
        )
        self.assertEqual(
            [ i.date.day for i in all_[2:6] ],
            [3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in all_[:-2] ],
            [1, 2, 3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in all_[2:] ],
            [3, 4, 5, 6, 7, 8]
        )
        self.assertEqual(
            [ i.date.day for i in all_[2:6:2] ],
            [3, 5]
        )
        limit_ = storage.query(None, limit=6)
        self.assertEqual(len(limit_), 6)
        self.assertEqual(
            [ i.date.day for i in limit_ ],
            [1, 2, 3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in limit_[1:5] ],
            [2, 3, 4, 5]
        )
        self.assertEqual(
            [ i.date.day for i in limit_[:-2] ],
            [1, 2, 3, 4]
        )
        self.assertEqual(
            [ i.date.day for i in limit_[2:] ],
            [3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in limit_[1:5:2] ],
            [2, 4]
        )
        start_ = storage.query(None, start=2)
        self.assertEqual(len(start_), 6)
        self.assertEqual(
            [ i.date.day for i in start_ ],
            [3, 4, 5, 6, 7, 8]
        )
        self.assertEqual(
            [ i.date.day for i in start_[1:5] ],
            [4, 5, 6, 7]
        )
        self.assertEqual(
            [ i.date.day for i in start_[:-2] ],
            [3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in start_[2:] ],
            [5, 6, 7, 8]
        )
        self.assertEqual(
            [ i.date.day for i in start_[1:5:2] ],
            [4, 6]
        )
        start_limit = storage.query(None, start=1, limit=7)
        self.assertEqual(len(start_limit), 6)
        self.assertEqual(
            [ i.date.day for i in start_limit ],
            [2, 3, 4, 5, 6, 7]
        )
        self.assertEqual(
            [ i.date.day for i in start_limit[1:5] ],
            [3, 4, 5, 6]
        )
        self.assertEqual(
            [ i.date.day for i in start_limit[:-2] ],
            [2, 3, 4, 5]
        )
        self.assertEqual(
            [ i.date.day for i in start_limit[2:] ],
            [4, 5, 6, 7]
        )
        self.assertEqual(
            [ i.date.day for i in start_limit[1:5:2] ],
            [3, 5]
        )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBooking))
    return suite
