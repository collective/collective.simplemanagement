from datetime import datetime
import unittest2 as unittest

from mock import patch

from ..interfaces import ITimeline
from ..timeline import BaseTimeline
from ..testing import BASE_INTEGRATION_TESTING


class DummyTimeline(BaseTimeline):

    indexes = ('a', 'b')

    def index(self, indexes, previous):
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
        timeline.snapshot()
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
        timeline.snapshot()
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
        timeline.snapshot()
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
        timeline.snapshot(indexes=['a'])
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
        timeline.snapshot(indexes=['b'])
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
        result = timeline.snapshot(insert=False)
        self.assertIn('a', timeline.data)
        self.assertIn('b', timeline.data)
        self.assertEqual(len(timeline.data['a'].items()), 0)
        self.assertEqual(len(timeline.data['b'].items()), 0)
        self.assertEqual(
            result,
            { 'a': 1, 'b': 1 }
        )

    def test_slice(self):
        pass


class TestIteration(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def test_create_iteration(self):
        pass

    def test_update_iteration(self):
        pass

    def test_add_story(self):
        pass

    def test_update_story(self):
        pass

    def test_delete_story(self):
        pass

    def test_move_in_story(self):
        pass

    def test_move_out_story(self):
        pass

    def test_add_booking(self):
        pass

    def test_update_booking(self):
        pass

    def test_remove_booking(self):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTimeline))
    suite.addTest(unittest.makeSuite(TestIteration))
    return suite
