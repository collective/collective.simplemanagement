# -*- coding: utf-8 -*-
import os.path
import unittest

import robotsuite
from ..testing import ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite(
            os.path.join("robotests", "project.robot")),
            layer=ROBOT_TESTING),
    ])

    return suite
