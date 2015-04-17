# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta

from zope.component import getMultiAdapter
# from zope.publisher.interfaces import NotFound
import plone.api
# from plone.memoize import view

from Products.Five.browser import BrowserView
# from Products.CMFPlone.utils import safe_unicode

from ... import _
from ... import api
from ... import mail_utils
# from ..widgets import book_widget


class View(BrowserView):
    """ iDoneThis
    """

    DATE_FORMAT = '%d/%m/%Y'
    show_form = True
    default_send_to = 'team@abstract.it'

    def __call__(self, send_email=False):
        if self.request.get('send_email') \
                and not send_email \
                and not self.request.get('search'):
            self.send_email()
        return super(View, self).__call__()

    @property
    def today(self):
        return datetime.now()

    @property
    def current_date(self):
        dt = self.today - timedelta(1)
        if self.request.get('by_date'):
            dt = self.request.get('by_date')
            dt = datetime.strptime(dt, self.DATE_FORMAT)
        return dt

    @property
    def current_date_display(self):
        return self.current_date.strftime(self.DATE_FORMAT)

    def date_range(self, dt):
        data = [
            dt.year,
            dt.month,
            dt.day
        ]
        start = data + [0, 0]
        stop = data + [23, 59]
        return (datetime(*start), datetime(*stop))

    @property
    def query(self):
        date_query = self.date_range(self.current_date)
        query = {
            'from_date': date_query[0],
            'to_date': date_query[1],
        }
        return query

    def data(self):
        bookings = {}
        users = {}
        all_bookings = api.booking.get_bookings(**self.query)
        for booking in all_bookings:
            if not booking.story and not booking.project:
                continue
            helpers = getMultiAdapter(
                (booking, self.request),
                name="helpers"
            )
            if booking.owner not in users:
                user_info = api.users.get_user_details(self.context,
                                                       booking.owner)
                users[booking.owner] = user_info
                bookings[booking.owner] = []
            bookings[booking.owner].append(
                helpers.info(user_details=False))
        return {
            'bookings': bookings,
            'users': users,
        }

    def send_email(self):
        mailhost = plone.api.portal.get_tool('MailHost')
        pprops = plone.api.portal.get_tool('portal_properties')
        mto = self.request.get('send_to', self.default_send_to)
        mfrom = pprops.email_from_address
        msubject = _(u"Abstract Team Done This") \
            + ' ' + self.current_date_display
        view = self.context.restrictedTraverse('@@idonethis-content')
        view.show_form = False
        html = view(send_email=True)
        html = mail_utils.prepare_email_content(
            html, mfrom, mto, msubject)
        mailhost.send(html, mto, mfrom, msubject)
