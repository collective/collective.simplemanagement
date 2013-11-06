# -*- coding: utf-8 -*-
from decimal import Decimal
from plone.testing import z2
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE


class BaseLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # pylint: disable=W0613
        # Load ZCML
        import collective.simplemanagement
        self.loadZCML(package=collective.simplemanagement, name='testing.zcml')
        z2.installProduct(app, 'Products.Poi')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.simplemanagement:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Project', 'test-project', title=u"Test project")
        test_project = portal['test-project']
        stories = []
        for i in xrange(1, 4):
            test_project.invokeFactory('Story', 'test-story-%d' % i,
                                       title=(u"Test story %d" % i))
            stories.append(test_project['test-story-%d' % i])
            stories[-1].estimate = Decimal(10 * i)
        setRoles(portal, TEST_USER_ID, ['Member'])


BASE = BaseLayer()


BASE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BASE,),
    name="collective.simplemanagement base integration testing"
)


BASE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BASE,),
    name="collective.simplemanagement base functional testing"
)


class BaseRobot(BaseLayer):
    defaultBases = (BASE, )

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.simplemanagement:default')

        # Set initial data
        self.applyProfile(portal, 'collective.simplemanagement:loadcontent')


BASE_ROBOT = BaseRobot()

ROBOT_TESTING = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE, BASE_ROBOT, z2.ZSERVER),
    name="collective.simplemenagement:Robot")
