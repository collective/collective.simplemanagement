import datetime
import json
from decimal import Decimal

from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from Products.Five.browser import BrowserView

from .. import logger
from ..bookingholes import create_hole
from ..story import create_story
from ..story import View as StoryView
from ..configure import Settings
from ..booking import BookingForm

from .engine import MacroRenderer


class Mixin(BrowserView):
    """ mixin klass for ajax views
    """

    _success = {
        'success': True,
        'error': None
    }

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.success = self._success.copy()

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
        data['estimate'] = Decimal(data['estimate'])
        create_story(self.context, data)
        return self.success


class AddBooking(Mixin):

    def process(self):
        form = BookingForm(self.context, self.request)
        form.update()
        return self.success


class ReloadBooking(Mixin):

    def process(self):
        view = self.context.restrictedTraverse('view')
        bookings = view.get_booking()
        template = PageTemplateFile("templates/macros.pt")
        renderer = MacroRenderer(template, 'booking-list', context=self.context)
        html = renderer(**dict(booking_list=bookings))
        self.success.update({'html': html})
        return self.success


class ReloadBookingForm(Mixin):

    def process(self):
        view = StoryView(self.context, self.request)
        self.success.update({'html': view.form_contents()})
        return self.success
