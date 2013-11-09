#-*- coding: utf-8 -*-

from collective.js.togetherjs.browser import Helpers

BLACKLISTED = (
    '@@compass',
    '@@worklog',
)

class Helpers(Helpers):
    """ override helpers view
    to blacklist some URLs to disable TogetherJS
    """

    def enabled(self):
        enabled = self.settings.enabled
        url = self.request.get('ACTUAL_URL')
        for item in BLACKLISTED:
            if item in url:
                enabled = False
                break
        return enabled
