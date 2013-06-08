import logging
from Products.CMFCore.utils import getToolByName



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
    if logger is None:
        logger = getLogger('collective.simplemanagement')
    logger.info("Reloading catalog")
    context.runImportStepFromProfile(DEFAULT_PROFILE, 'catalog')
    logger.info("Reindexing projects")
    pc = getToolByName(context, 'portal_catalog')
    for brain in pc.searchResults(portal_type='Project'):
        project = brain.getObject()
        project.reindexObject()
