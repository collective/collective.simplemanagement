# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger('[sm.idonethis]')

from datetime import datetime
from datetime import timedelta

from zope.component import getMultiAdapter
# from zope.publisher.interfaces import NotFound
import plone.api
from plone.memoize import view

from Products.Five.browser import BrowserView
# from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage

from ... import _
from ... import api
from ... import mail_utils
from ...utils import LazyList


class View(BrowserView):
    """ iDoneThis
    """

    DATE_FORMAT = '%d/%m/%Y'
    show_form = True
    default_send_to = 'Team <team@abstract.it>'

    @property
    def today(self):
        return datetime.now()

    @property
    def current_date(self):
        # default to the day before today
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

    def formatter(self, booking):
        helpers = getMultiAdapter(
            (booking, self.request),
            name="helpers"
        )
        info = helpers.info(user_details=False,
                            drop_refs_links=True,
                            minimal=True)
        return info

    @view.memoize
    def get_bookings(self):
        return api.booking.get_bookings(**self.query)

    def data(self):
        users = {}
        bookings = {}
        for booking in self.get_bookings():
            if not booking.story and not booking.project:
                continue

            if booking.owner not in users:
                user_info = api.users.get_user_details(self.context,
                                                       booking.owner)
                users[booking.owner] = user_info
                bookings[booking.owner] = LazyList(
                    [], format_method=self.formatter)
            bookings[booking.owner].append(booking)
        return {
            'users': sorted(users.itervalues(), key=lambda x: x.fullname),
            'bookings': bookings,
        }


class SendEmail(View):

    redirect = True

    def __call__(self):
        if self.request.get('send_email'):
            return self.send_email()
        return "confirm send by providing `send_email` key"

    def send_email(self):
        view = self.context.restrictedTraverse('@@idonethis-content')
        bookings = view.get_bookings()
        status = 'ok'
        if not len(bookings) > 0:
            status = 'nobookings'
            logger.info('no bookings found...')
        else:
            view.show_form = False
            html = view()

            mailhost = plone.api.portal.get_tool('MailHost')
            pprops = plone.api.portal.get_tool('portal_properties')
            mto = self.request.get('send_to', self.default_send_to)
            mfrom = 'SM <{}>'.format(pprops.email_from_address)
            msubject = _(u"Abstract Team Done This") \
                + ' ' + self.current_date_display
            html = mail_utils.prepare_email_content(
                html, mfrom, mto, msubject)

            mailhost.send(html, mto, mfrom, msubject)
            logger.info('mail sent')
        if self.redirect and self.request.get('status_message'):
            if status == 'ok':
                msg = _('Email sent.')
            else:
                msg = _('No bookings, no email send.')
            messages = IStatusMessage(self.request)
            messages.add(msg, type="info")
            url = self.context.absolute_url() + '/@@idonethis'
            if self.request.get('QUERY_STRING'):
                qstring = self.request['QUERY_STRING'].split('&send_email')[0]
                url += '?' + qstring
            self.request.response.redirect(url)
            return
        else:
            return status


class CronView(SendEmail):

    redirect = False
    DATE_FORMAT = '%d/%m/%Y'

    def __call__(self):
        today = datetime.today()
        weekday = today.weekday()
        # TODO: exclude holidays!
        if weekday in (5, 6):
            # sat or sun
            return
        if weekday == 0:
            # monday, we want friday
            dt = today - timedelta(3)
            by_date = dt.strftime(self.DATE_FORMAT)
            self.request.form['by_date'] = by_date
        return self.send_email()
