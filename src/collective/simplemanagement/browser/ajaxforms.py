import datetime
import json
from decimal import Decimal

from Products.Five.browser import BrowserView
from ..bookingholes import create_hole
from ..story import create_story
from ..configure import Settings
from .. import logger


class Mixin(BrowserView):
    """ mixin klass for ajax views
    """

    success = {
        'success': True,
        'error': None
    }

    def __call__(self):
        try:
            result = self.process()
        except Exception, e:  # pylint: disable=W0703
            logger.exception(self.error_msg)
            result = {
                'success': False,
                'error': str(e)
            }
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)

    def process(self):
        """ process ajax request
        """
        raise NotImplementedError("You mus provide a `process` method!")

    @property
    def error_msg(self):
        return "An error occurred while processing '%s' view" % self.__name__

    @property
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')


class CreateHole(Mixin):

    def process(self):
        date = [int(x) for x in self.request['date'].split('-')]
        date = datetime.date(*date),
        time = int(self.request['time'])
        reason = self.request['reason']

        settings = Settings()
        missing_time = settings.man_day_hours - time
        missing_time = Decimal(missing_time)
        member = self.portal_state.member()
        # create hole
        create_hole(date,
                    missing_time,
                    member.getId(),
                    reason=reason)
        return self.success


class AddStory(Mixin):

    def process(self):
        form = self.request.form
        data = {}
        for i in ('title', 'estimate'):
            data[i] = form.get("form.widgets.%s" % i)
        create_story(self.context, data)
        return self.success
