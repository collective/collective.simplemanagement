import logging
import plone.api

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName

from .interfaces.compass import ICompassSettings
from .interfaces.project import IProject


# pylint: disable=W0613


LOGGER = 'collective.simplemanagement'
DEFAULT_PROFILE = 'profile-collective.simplemanagement:default'


def getLogger(logger=None):
    if logger is None:
        logger = logging.getLogger(LOGGER)
    return logger


def upgrade_to_1001(context, logger=None):
    logger = getLogger(logger)
    logger.info("Create order_number index")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'catalog')

    logger.info("Reindex order_number index")
    pc = getToolByName(context, 'portal_catalog')
    pc.reindexIndex('order_number', context.REQUEST)


def upgrade_to_1002(context, logger=None):
    logger = getLogger(logger)
    logger.info("Adding records to the registry")
    registry = getUtility(IRegistry)
    registry.registerInterface(ICompassSettings)
    proxy = registry.forInterface(ICompassSettings)
    proxy.default_plan_length = 2
    proxy.minimum_plan_length = 1
    proxy.maximum_plan_length = 4
    logger.info("Reloading javascript registry")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'jsregistry')
    logger.info("Reloading catalog")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'catalog')
    logger.info("Rebuilding catalog")
    pc = getToolByName(context, 'portal_catalog')
    pc.clearFindAndRebuild()
    logger.info("Creating portal tool")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'toolset')


def upgrade_to_1003(context, logger=None):
    logger = getLogger(logger)
    logger.info("Fixing registry")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'plone.app.registry')
    logger.info("Reloading javascript registry")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'jsregistry')
    to_remove = (
        "++resource++simplemanagement/jquery.drawer.js",
        "++resource++simplemanagement/simplemanagement.js",
        "++resource++simplemanagement/worklog.js",
        "++resource++simplemanagement/ICanHaz.js",
        "++resource++simplemanagement/json2.js",
        "++resource++simplemanagement/knockout-2.2.1.js",
        "++resource++simplemanagement/knockout-sortable.js",
        "++resource++simplemanagement/compass.js",
    )
    jstool = getToolByName(context, 'portal_javascripts')
    for res in to_remove:
        jstool.unregisterResource(res)
        logger.info("removed %s" % res)
    jstool.cookResources()

    logger.info("removing stylesheets")
    to_remove = (
        '++resource++simplemanagement/simplemanagement.css',
    )
    csstool = getToolByName(context, 'portal_css')
    for res in to_remove:
        csstool.unregisterResource(res)
        logger.info("removed %s" % res)
    csstool.cookResources()


def upgrade_to_1004(context, logger=None):
    logger = getLogger(logger)
    logger.info("Fixing bad values in projects operatives")
    acl_users = plone.api.portal.get_tool(name='acl_users')
    catalog = plone.api.portal.get_tool(name='portal_catalog')
    for brain in catalog(object_provides=IProject.__identifier__):
        obj = brain.getObject()
        if not obj.operatives:
            continue
        for op in obj.operatives:
            userid = op.user_id
            if not acl_users.getUserById(userid):
                # we do not have a valid userid here
                # and we suppose to have a fullname in it
                logger.info('fixing operative "%s" for project %s' % (userid,
                                                                    brain.getPath()))
                user = acl_users.searchUsers(fullname=userid)
                if user:
                    new_userid = user[0]['userid']
                    logger.info('operative %s => %s' % (userid, new_userid))
                    op.user_id = new_userid
                else:
                    logger.info('replacement for operative "%s" NOT FOUND' % (userid))


def upgrade_to_1005(context, logger=None):
    logger = getLogger(logger)
    logger.info("Adding actions")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'actions')


def upgrade_to_1006(context, logger=None):
    logger = getLogger(logger)
    logger.info("Refreshing actions")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'actions')
    logger.info("Refreshing role mappings")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'rolemap')


def upgrade_to_1007(context, logger=None):
    logger = getLogger(logger)
    logger.info("Reloading javascript registry")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'jsregistry')


def upgrade_to_1008(context, logger=None):
    logger = getLogger(logger)
    logger.info("install collective.select2")
    qi = getToolByName(context, 'portal_quickinstaller')
    qi.installProduct('collective.select2')


def upgrade_to_1009(context, logger=None):
    logger = getLogger(logger)
    logger.info("Update behaviors")

    new_behavior = "collective.simplemanagement.interfaces.ordernumber.IOrderNumber"

    types = [
        'Story',
        'Project',
        'Iteration',
        'Epic',
    ]

    for name in types:
        fti = getUtility(IDexterityFTI, name=name)
        behaviors = list(fti.behaviors)
        if new_behavior not in behaviors:
            behaviors.append(new_behavior)
        fti.behaviors = behaviors

    logger.info("Importing viewlets")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'viewlets')


def upgrade_to_1010(context, logger=None):
    logger = getLogger(logger)
    logger.info("Installing utility")
    context.runImportStepFromProfile(
        DEFAULT_PROFILE,
        'collective.simplemanagement.booking.install'
    )
    logger.info("Reloading rolemap")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'rolemap')
    logger.info("Reloading javascript registry")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'jsregistry')
    logger.info("Adding actions")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'actions')
    logger.info("Reloading catalog definition")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'catalog')
    logger.info("Cleaning up configuration registry")
    registry = getUtility(IRegistry)
    prefix = 'collective.simplemanagement.interfaces.settings.ISettings.'
    del registry.records[prefix+'booking_check_delta_days_start']
    del registry.records[prefix+'booking_check_delta_days_end']
    del registry.records[prefix+'off_duty_reasons']
    logger.info("Rebuilding catalog")
    portal_catalog = getToolByName(context, 'portal_catalog')
    portal_catalog.clearFindAndRebuild()


def upgrade_to_1011(context, logger=None):
    logger = getLogger(logger)
    logger.info('Removing xregexp js')
    portal_javascripts = getToolByName(context, 'portal_javascripts')
    portal_javascripts.unregisterResource(
        '++resource++simplemanagement/js/xregexp.js'
    )


def upgrade_to_1012(context, logger=None):
    logger = getLogger(logger)
    logger.info('Disabling jQueryUI autocomplete')
    # jQueryUI autocomplete destroys the autocomplete used by contenttree
    registry = getUtility(IRegistry)
    key = (
        'collective.js.jqueryui.controlpanel.IJQueryUIPlugins.ui_autocomplete'
    )
    registry[key] = False


def upgrade_to_1013(context, logger=None):
    logger = getLogger(logger)
    logger.info('Install collective.z3cform.datagridfield')

    qi = getToolByName(context, 'portal_quickinstaller')
    qi.installProduct('collective.z3cform.datagridfield')
