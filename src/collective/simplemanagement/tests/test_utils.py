import datetime
import unittest2 as unittest

from ..testing import BASE_INTEGRATION_TESTING
from .. import utils


class TestBaseUtils(unittest.TestCase):

    def test_boolize(self):
        pass

    def test_difference_class(self):
        pass

    def test_get_ancestor(self):
        pass

    def test_datetimerange(self):
        start = datetime.date(2013, 6, 1)
        stop = datetime.date(2013, 6, 11)
        _range = utils.datetimerange(start, stop)
        dates = [x[0] for x in _range]
        assert len(dates) == 10, 'expected 10 dates, got %s' % len(dates)
        for i in xrange(1, 11):
            adate = datetime.date(2013, 6, i)
            assert adate in dates, 'date %s not in range' % adate.strftime('%Y%m%d')

        _range = utils.datetimerange(start, stop, exclude_weekend=True)
        dates = [x[0] for x in _range]
        excluded = (
            datetime.date(2013, 6, 1),  # saturday
            datetime.date(2013, 6, 2),  # sunday
            datetime.date(2013, 6, 8),  # saturday
            datetime.date(2013, 6, 9),  # sunday
        )
        assert len(dates) == 6, 'expected 6 dates, got %s' % len(dates)
        for adate in excluded:
            assert adate not in dates, 'date %s in range' % adate.strftime('%Y%m%d')


class TestContentUtils(unittest.TestCase):

    layer = BASE_INTEGRATION_TESTING

    def test_get_project(self):
        pass

    def test_get_iteration(self):
        pass

    def test_get_timings(self):
        pass

    def test_get_user_details(self):
        pass

    def test_get_epic_by_story(self):
        pass

    def test_get_text(self):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBaseUtils))
    suite.addTest(unittest.makeSuite(TestContentUtils))
    return suite
