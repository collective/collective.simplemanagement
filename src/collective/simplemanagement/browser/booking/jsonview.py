import json
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from zope.security import checkPermission
from Products.Five.browser import BrowserView
from plone import api as plone_api

from ... import api
from ..widgets import book_widget

# BBB: REMOVE BUT TAKE INSPIRATION FROM checkPermission CODE

@implementer(IPublishTraverse)
class Main(BrowserView):

    def publishTraverse(self, request, name): # pylint: disable=unused-argument
        if not hasattr(self, 'booking'):
            self.uuid = booking_uid = name
            self.storage = api.booking.get_booking_storage()
            if booking_uid in self.storage.bookings:
                self.booking = self.storage.bookings[booking_uid]
                return self
        raise NotFound(name)

    def __call__(self):
        if not hasattr(self, 'booking') or not getattr(self, 'booking'):
            raise NotFound(self.uuid)
        self.request.response.setHeader('Content-Type', 'application/json')
        is_anonymous = plone_api.user.is_anonymous()
        is_manager = False
        current_user = None
        if not is_anonymous:
            is_manager = checkPermission(self.context, 'cmf.ManagePortal')
            current_user = plone_api.user.get_current()
        else:
            raise NotFound(self.uuid)
        if self.request.method == 'GET':
            data = self.booking.as_dict()
            data['rendered_text'] = book_widget.format_text(self.booking)
            return json.dumps(data, cls=api.jsonutils.ExtendedJSONEncoder)
        else:
            if self.booking.owner != current_user.id and not is_manager:
                self.request.response.setStatus(403)
                return json.dumps({'status': 'fail',
                                   'reason': 'Missing permission'})
            data = self.request.form
            if '_delete' in data:
                if data['_delete'] == self.uuid:
                    self.storage.delete(self.uuid)
                    return json.dumps({'status': 'ok'})
                self.request.response.setStatus(400)
                return json.dumps({'status': 'fail',
                                   'reason': 'Malformed delete request'})
