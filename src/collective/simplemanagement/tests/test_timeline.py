from datetime import date, datetime, timedelta
from decimal import Decimal

import unittest2 as unittest
from mock import patch

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone.app.testing import (TEST_USER_ID, TEST_USER_NAME, login, setRoles)

from ..interfaces import ITimeline
from ..timeline import BaseTimeline
from ..testing import BASE_INTEGRATION_TESTING


DUMMY_CONTEXT = object()


class DummyTimeline(BaseTimeline):

    indexes = ('a', 'b')

    def index(self, context, indexes, previous):
        assert context is DUMMY_CONTEXT
        result = {}
        for index in indexes:
            result[index] = 1 if previous[index] is None else \
                previous[index] + 1
        return result


class TestTimeline(unittest.TestCase):

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_snapshot_full(self, mock_datetime):
        now = datetime(2012, 12, 15, 0, 0, 0)
        mock_datetime.now.return_value = now
        timeline = DummyTimeline()
        self.assertNotIn('a', timeline.data)
        self.assertNotIn('b', timeline.data)
        timeline.snapshot(DUMMY_CONTEXT)
        self.assertIn('a', timeline.data)
        self.assertIn('b', timeline.data)
        self.assertEqual(
            tuple(timeline.data['a'].items()),
            ((now, 1),)
        )
        self.assertEqual(
            tuple(timeline.data['b'].items()),
            ((now, 1),)
        )
        before = now
        now = datetime(2012, 12, 16, 0, 0, 0)
        mock_datetime.now.return_value = now
        timeline.snapshot(DUMMY_CONTEXT)
        self.assertEqual(
            tuple(timeline.data['a'].items()),
            ((before, 1), (now, 2))
        )
        self.assertEqual(
            tuple(timeline.data['b'].items()),
            ((before, 1), (now, 2))
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_snapshot_partial(self, mock_datetime):
        one = datetime(2012, 12, 15, 0, 0, 0)
        mock_datetime.now.return_value = one
        timeline = DummyTimeline()
        self.assertNotIn('a', timeline.data)
        self.assertNotIn('b', timeline.data)
        timeline.snapshot(DUMMY_CONTEXT)
        self.assertIn('a', timeline.data)
        self.assertIn('b', timeline.data)
        self.assertEqual(
            tuple(timeline.data['a'].items()),
            ((one, 1),)
        )
        self.assertEqual(
            tuple(timeline.data['b'].items()),
            ((one, 1),)
        )
        two = datetime(2012, 12, 16, 0, 0, 0)
        mock_datetime.now.return_value = two
        timeline.snapshot(DUMMY_CONTEXT, indexes=['a'])
        self.assertEqual(
            tuple(timeline.data['a'].items()),
            ((one, 1), (two, 2))
        )
        self.assertEqual(
            tuple(timeline.data['b'].items()),
            ((one, 1),)
        )
        three = datetime(2012, 12, 17, 0, 0, 0)
        mock_datetime.now.return_value = three
        timeline.snapshot(DUMMY_CONTEXT, indexes=['b'])
        self.assertEqual(
            tuple(timeline.data['a'].items()),
            ((one, 1), (two, 2))
        )
        self.assertEqual(
            tuple(timeline.data['b'].items()),
            ((one, 1), (three, 2))
        )

    def test_snapshot_noinsert(self):
        timeline = DummyTimeline()
        self.assertNotIn('a', timeline.data)
        self.assertNotIn('b', timeline.data)
        result = timeline.snapshot(DUMMY_CONTEXT, insert=False)
        self.assertIn('a', timeline.data)
        self.assertIn('b', timeline.data)
        self.assertEqual(len(timeline.data['a'].items()), 0)
        self.assertEqual(len(timeline.data['b'].items()), 0)
        self.assertEqual(
            result,
            { 'a': 1, 'b': 1 }
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_slice(self, mock_datetime):
        timeline = DummyTimeline()
        for day in xrange(1, 32):
            mock_datetime.now.return_value = datetime(2012, 12, day, 0, 0, 0)
            timeline.snapshot(DUMMY_CONTEXT)
        weekly = timeline.slice(
            datetime(2012, 12, 3),
            datetime(2012, 12, 31),
            timedelta(days=7)
        )
        self.assertEqual(
            [ t for t in weekly ],
            [
                (datetime(2012, 12, 3), { 'a': 9, 'b': 9 }),
                (datetime(2012, 12, 10), { 'a': 16, 'b': 16 }),
                (datetime(2012, 12, 17), { 'a': 23, 'b': 23 }),
                (datetime(2012, 12, 24), { 'a': 30, 'b': 30 }),
            ]
        )
        daily = timeline.slice(
            datetime(2012, 12, 3),
            datetime(2012, 12, 7),
            timedelta(days=1)
        )
        self.assertEqual(
            [ t for t in daily ],
            [
                (datetime(2012, 12, 3), { 'a': 3, 'b': 3 }),
                (datetime(2012, 12, 4), { 'a': 4, 'b': 4 }),
                (datetime(2012, 12, 5), { 'a': 5, 'b': 5 }),
                (datetime(2012, 12, 6), { 'a': 6, 'b': 6 }),
            ]
        )
        hourly = timeline.slice(
            datetime(2012, 12, 3, 22),
            datetime(2012, 12, 4, 2),
            timedelta(hours=1)
        )
        self.assertEqual(
            [ t for t in hourly ],
            [
                (datetime(2012, 12, 3, 22), { 'a': 3, 'b': 3 }),
                (datetime(2012, 12, 3, 23), { 'a': 3, 'b': 3 }),
                (datetime(2012, 12, 4, 0), { 'a': 4, 'b': 4 }),
                (datetime(2012, 12, 4, 1), { 'a': 4, 'b': 4 }),
            ]
        )


class TestIteration(unittest.TestCase):

    maxDiff = None

    layer = BASE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.project = self.portal['test-project']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def assertTimelineEqual(self, object_, from_, to, step, list_):
        timeline = ITimeline(object_)
        self.assertEqual(
            [ e for e in timeline.slice(from_, to, step) ],
            list_
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_create_iteration(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 29),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_update_iteration(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.estimate = Decimal("2.0")
        notify(ObjectModifiedEvent(iteration_1))
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 30),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("16.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_add_story(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 30),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_update_story(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        story_1_1 = iteration_1['story-1-1']
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        story_1_1.estimate = Decimal("7.00")
        notify(ObjectModifiedEvent(story_1_1))
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 31),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("7.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_delete_story(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        iteration_1.manage_delObjects(['story-1-1'])
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 31),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_move_in_story(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        clipboard = self.project.manage_cutObjects(ids=['test-story-1'])
        iteration_1.manage_pasteObjects(clipboard)
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 30),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("10.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_move_out_story(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        clipboard = iteration_1.manage_cutObjects(ids=['story-1-1'])
        self.project.manage_pasteObjects(clipboard)
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 31),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_add_booking(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        story_1_1 = iteration_1['story-1-1']
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        story_1_1.invokeFactory('Booking',
                                'booking-1',
                                title=u"Booking 1",
                                date=date(2012, 12, 30),
                                time=Decimal("1.00"))
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2012, 12, 31),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("1.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_update_booking(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        story_1_1 = iteration_1['story-1-1']
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        story_1_1.invokeFactory('Booking',
                                'booking-1',
                                title=u"Booking 1",
                                date=date(2012, 12, 30),
                                time=Decimal("1.00"))
        booking_1 = story_1_1['booking-1']
        mock_datetime.now.return_value = datetime(2012, 12, 31, 8, 0, 0)
        booking_1.time = Decimal("8.00")
        notify(ObjectModifiedEvent(booking_1))
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2013, 1, 1),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("1.00") }),
                (datetime(2012, 12, 31), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("8.00") })
            ]
        )

    @patch('collective.simplemanagement.timeline.datetime', autospec=True)
    def test_remove_booking(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2012, 12, 28, 8, 0, 0)
        self.project.invokeFactory('Iteration',
                                   'iteration-1',
                                   title=u"Iteration 1",
                                   start=date(2012, 12, 28),
                                   end=date(2012, 12, 31),
                                   estimate=Decimal("1.00"))
        iteration_1 = self.project['iteration-1']
        mock_datetime.now.return_value = datetime(2012, 12, 29, 8, 0, 0)
        iteration_1.invokeFactory('Story',
                                  'story-1-1',
                                  title=u"Story 1.1",
                                  estimate=Decimal("8.00"))
        story_1_1 = iteration_1['story-1-1']
        mock_datetime.now.return_value = datetime(2012, 12, 30, 8, 0, 0)
        story_1_1.invokeFactory('Booking',
                                'booking-1',
                                title=u"Booking 1",
                                date=date(2012, 12, 30),
                                time=Decimal("1.00"))
        mock_datetime.now.return_value = datetime(2012, 12, 31, 8, 0, 0)
        story_1_1.manage_delObjects(['booking-1'])
        self.assertTimelineEqual(
            iteration_1,
            datetime(2012, 12, 28),
            datetime(2013, 1, 1),
            timedelta(days=1),
            [
                (datetime(2012, 12, 28), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("0.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 29), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") }),
                (datetime(2012, 12, 30), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("1.00") }),
                (datetime(2012, 12, 31), { 'estimate': Decimal("8.00"),
                                           'todo': Decimal("8.00"),
                                           'done': Decimal("0.00") })
            ]
        )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTimeline))
    suite.addTest(unittest.makeSuite(TestIteration))
    return suite
