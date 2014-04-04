# from datetime import date
# from decimal import Decimal

# import unittest2 as unittest
# from zope.component import getUtility

# from plone.app.testing.interfaces import TEST_USER_ID

# from ..interfaces import IBookingHoles
# from ..bookingholes import BookingHole
# from ..testing import BASE_INTEGRATION_TESTING


# class TestBookingHoles(unittest.TestCase):

#     layer = BASE_INTEGRATION_TESTING

#     def test_get_utility(self):
#         utility = getUtility(IBookingHoles)
#         self.assertTrue(IBookingHoles.providedBy(utility))

#     def test_add_hole(self):
#         utility = getUtility(IBookingHoles)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("8.00"),
#             TEST_USER_ID,
#             reason=u"sick"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 1)
#         with self.assertRaises(AssertionError):
#             utility.add(object())
#         self.assertEqual(len(utility), 1)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("4.00"),
#             TEST_USER_ID,
#             reason=u"leave"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 1)
#         hole = [ h for h in utility][0]
#         self.assertEqual(hole.reason, u"leave")
#         self.assertEqual(hole.hours, Decimal("4.0"))

#     def test_length(self):
#         utility = getUtility(IBookingHoles)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("8.00"),
#             'user_1',
#             reason=u"sick"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 1)
#         hole = BookingHole(
#             date(2012, 12, 29),
#             Decimal("8.00"),
#             'user_1',
#             reason=u"sick"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 2)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("8.00"),
#             'user_2',
#             reason=u"sick"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 3)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("4.00"),
#             'user_1',
#             reason=u"leave"
#         )
#         utility.add(hole)
#         self.assertEqual(len(utility), 3)

#     def test_remove_hole(self):
#         utility = getUtility(IBookingHoles)
#         for user in ['user_1', 'user_2']:
#             for day in [28, 29, 30]:
#                 hole = BookingHole(
#                     date(2012, 12, day),
#                     Decimal("8.00"),
#                     user,
#                     reason=u"sick"
#                 )
#                 utility.add(hole)
#         self.assertEqual(len(utility), 6)
#         utility.remove('user_1', day=date(2012, 12, 29))
#         self.assertEqual(len(utility), 5)
#         utility.remove('user_2')
#         self.assertEqual(len(utility), 2)
#         with self.assertRaises(KeyError):
#             utility.remove('user_1', day=date(2012, 12, 12))
#         with self.assertRaises(KeyError):
#             utility.remove('user_3', day=date(2012, 12, 28))
#         with self.assertRaises(KeyError):
#             utility.remove('user_3')
#         holes = [ (h.day, h.user_id) for h in utility ]
#         self.assertItemsEqual(
#             [ (date(2012, 12, 28), 'user_1'), (date(2012, 12, 30), 'user_1') ],
#             holes
#         )

#     def test_contains(self):
#         utility = getUtility(IBookingHoles)
#         hole = BookingHole(
#             date(2012, 12, 28),
#             Decimal("8.00"),
#             TEST_USER_ID,
#             reason=u"sick"
#         )
#         utility.add(hole)
#         self.assertIn(TEST_USER_ID, utility)
#         self.assertNotIn('completely_unplausible_user_id', utility)

#     def test_iter(self):
#         utility = getUtility(IBookingHoles)
#         for user in ['user_1', 'user_2']:
#             for day in [28, 29, 30]:
#                 hole = BookingHole(
#                     date(2012, 12, day),
#                     Decimal("8.00"),
#                     user,
#                     reason=u"sick"
#                 )
#                 utility.add(hole)
#         self.assertItemsEqual(
#             [
#                 (date(2012, 12, 28), 'user_1'),
#                 (date(2012, 12, 29), 'user_1'),
#                 (date(2012, 12, 30), 'user_1'),
#                 (date(2012, 12, 28), 'user_2'),
#                 (date(2012, 12, 29), 'user_2'),
#                 (date(2012, 12, 30), 'user_2'),
#             ],
#             [ (h.day, h.user_id) for h in utility ]
#         )

#     def test_iter_user(self):
#         utility = getUtility(IBookingHoles)
#         for day in [7, 12, 13, 18, 20, 21, 22, 23, 28]:
#             hole = BookingHole(
#                 date(2012, 12, day),
#                 Decimal("8.00"),
#                 TEST_USER_ID,
#                 reason=u"sick"
#             )
#             utility.add(hole)
#         self.assertEqual(
#             [ ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 3),
#                                                    date(2012, 12, 6)) ]
#         )
#         self.assertEqual(
#             [ 7 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 3),
#                                                    date(2012, 12, 7)) ]
#         )
#         self.assertEqual(
#             [ 7, 12 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 3),
#                                                    date(2012, 12, 12)) ]
#         )
#         self.assertEqual(
#             [ 12, 13, 18, 20 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 10),
#                                                    date(2012, 12, 20)) ]
#         )
#         self.assertEqual(
#             [ 12, 13, 18 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 10),
#                                                    date(2012, 12, 19)) ]
#         )
#         self.assertEqual(
#             [ 23, 28 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 23),
#                                                    date(2012, 12, 31)) ]
#         )
#         self.assertEqual(
#             [ 28 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 25),
#                                                    date(2012, 12, 31)) ]
#         )
#         self.assertEqual(
#             [ 28 ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 28),
#                                                    date(2012, 12, 31)) ]
#         )
#         self.assertEqual(
#             [ ],
#             [ h.day.day for h in utility.iter_user(TEST_USER_ID,
#                                                    date(2012, 12, 29),
#                                                    date(2012, 12, 31)) ]
#         )
#         self.assertEqual(
#             [ ],
#             [ h.day.day for h in utility.iter_user('nonexisting_user',
#                                                    date(2012, 12, 10),
#                                                    date(2012, 12, 20)) ]
#         )


# def test_suite():
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(TestBookingHoles))
#     return suite
