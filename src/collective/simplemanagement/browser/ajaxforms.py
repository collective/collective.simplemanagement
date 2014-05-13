#-*- coding: utf-8 -*-
import json

from Products.Five.browser import BrowserView

from .. import logger
from .story.view import View as StoryView
from ..booking import BookingForm
from .. import _
from .. import api


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
        return json.dumps(result, cls=api.jsonutils.ExtendedJSONEncoder)

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


class AddBooking(Mixin):

    FormKlass = BookingForm


class ReloadBooking(Mixin):

    def process(self):
        view = self.context.restrictedTraverse('view')
        bookings = view.get_booking()[:5]
        timing = view.timing()

        self.success.update({
            'bookings': bookings,
            'timing': timing
        })
        return self.success


class ReloadBookingForm(Mixin):

    def _process(self):
        view = StoryView(self.context, self.request)
        self.success.update({'html': view.form_contents()})
        return self.success
