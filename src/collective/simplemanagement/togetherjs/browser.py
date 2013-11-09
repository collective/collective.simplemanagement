#-*- coding: utf-8 -*-

from collective.js.togetherjs.browser import Helpers as BaseHelpers

BLACKLISTED = (
    '@@compass',
    '@@worklog',
)

class Helpers(BaseHelpers):
    """ override helpers view
    to blacklist some URLs to disable TogetherJS
    """

    def enabled(self):
        enabled = super(Helpers, self).enabled()
        url = self.request.get('ACTUAL_URL')
        for item in BLACKLISTED:
            if item in url:
                enabled = False
                break
        return enabled
