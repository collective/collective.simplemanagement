import logging

from zope.i18nmessageid import MessageFactory

messageFactory = MessageFactory('collective.simplemanagement')
_ = messageFactory

logger = logging.getLogger('collective.simplemanagement')


# Load content utils
from .loadcontent import set_operatives
from .loadcontent import set_environments
from .loadcontent import set_milestones
from .loadcontent import convert_date
