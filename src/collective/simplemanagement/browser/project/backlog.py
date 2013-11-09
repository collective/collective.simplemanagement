from Products.Five.browser import BrowserView
from zope.interface import implementer
from ...interfaces import IBacklogView
from ..iteration.base import IterationViewMixin


@implementer(IBacklogView)
class Backlog(BrowserView, IterationViewMixin):
    pass
