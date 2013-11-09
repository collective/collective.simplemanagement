import logging
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from .interfaces.compass import ICompassSettings



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
