from Products.Five.browser import BrowserView
from ..utils import timeago


class Helper(BrowserView):

    def timeago(self, timestamp):
        return timeago(timestamp)
