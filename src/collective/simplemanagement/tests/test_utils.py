import unittest2 as unittest

from ..testing import BASE_INTEGRATION_TESTING


class TestBaseUtils(unittest.TestCase):

    def test_boolize(self):
        pass

    def test_difference_class(self):
        pass

    def test_datetimerange(self):
        pass

    def test_get_ancestor(self):
        pass


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
