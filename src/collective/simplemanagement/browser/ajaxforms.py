#-*- coding: utf-8 -*-

import datetime
import json
from decimal import Decimal

from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from Products.Five.browser import BrowserView

from .. import logger
from ..bookingholes import create_hole
from ..story import View as StoryView
from ..story import StoryQuickForm
from ..configure import Settings
from ..booking import BookingForm
from .. import _
from .engine import MacroRenderer


class Mixin(BrowserView):
    """ mixin klass for ajax views
    """

    _success = {
        'success': True,
        'error': None,
        'result': None,
    }
    FormKlass = None
    creation_form = False
    created_message = _(u'Created:')

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
                'error': self.error_msg + '\n' + str(e)
            }
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)

    def process(self):
        FormKlass = getattr(self, 'FormKlass')
        if FormKlass is not None:
            form = FormKlass(self.context, self.request)
            form.update()
            data, errors = form.extractData()
            if not errors:
                if self.creation_form and form.created:
                    self.success.update({
                        'result': {
                            'created': {
                                'msg': self.created_message,
                                'title': form.created.title,
                                'url': form.created.absolute_url(),
                            }
                        }
                    })
                return self.success
            else:
                info = []
                for err in errors:
                    info.append({
                        'message': err.message,
                        'fieldname': err.widget.field.__name__,
                        'label': err.widget.label,
                    })
                self.success['errors'] = info
                self.success['error'] = True
                return self.success
        return self._process()

    def _process(self):
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
        # TODO: use a form in here
        date = [int(x) for x in self.request['date'].split('-')]
        date = datetime.date(*date)
        time = Decimal(self.request['time'])
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

    FormKlass = StoryQuickForm
    creation_form = True
    created_message = _(u'Created story:')


class AddBooking(Mixin):

    FormKlass = BookingForm


class ReloadStories(Mixin):
    # XXX: TODO!

    def process(self):
        # view = self.context.restrictedTraverse('view')
        # template = PageTemplateFile("templates/macros.pt")

        # stories = view.get_stories()
        # renderer = MacroRenderer(template, 'stories-list', context=self.context)
        # stories_html = renderer(**dict(stories_list=stories))

        # self.success.update({
        #     'stories_html': stories_html,
        # })
        return self.success


class ReloadBooking(Mixin):

    def process(self):
        view = self.context.restrictedTraverse('view')
        template = PageTemplateFile("templates/macros.pt")

        bookings = view.get_booking()
        renderer = MacroRenderer(template, 'booking-list', context=self.context)
        bookings_html = renderer(**dict(booking_list=bookings))

        timing = view.timing()
        renderer = MacroRenderer(template, 'story-timing', context=self.context)
        timing_html = renderer(**dict(timing=timing))

        self.success.update({
            'bookings_html': bookings_html,
            'timing_html': timing_html
        })
        return self.success


class ReloadBookingForm(Mixin):

    def _process(self):
        view = StoryView(self.context, self.request)
        self.success.update({'html': view.form_contents()})
        return self.success
