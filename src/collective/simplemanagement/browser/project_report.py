import datetime
import calendar
from decimal import Decimal

from plone.memoize.view import memoize as view_memoize

from .. import api
from ..interfaces import IProject
from ..utils import AttrDict

from dashboard import DashboardMixin
from worklog import MONTHS


class ReportView(DashboardMixin):
    """ a report view for projects and stories
    """

    @property
    def _defaults(self):
        today = datetime.date.today()
        return {
            'month': today.month,
            'year': today.year,
            'employee': ''
        }

    @property
    def selected(self):
        data = AttrDict()
        for k in ('month', 'year', 'employee'):
            data[k] = self.request.get(k) or self._defaults.get(k)
        return data

    @property
    def months(self):
        for i, month in enumerate(MONTHS):
            num = i + 1
            req_val = self.selected.month
            selected = None
            if req_val != 'all':
                selected = int(req_val) == num
            yield {
                'value': num,
                'label': month,
                'selected': selected
            }

    @property
    def years(self):
        today = datetime.date.today()
        for i in xrange(today.year - 2, today.year + 1):
            yield {
                'value': i,
                'label': i,
                'selected': int(self.request.get('year', self.selected.year)) == i
            }

    @property
    @view_memoize
    def project(self):
        return api.content.get_project(self.context)

    @property
    def is_project(self):
        return IProject.providedBy(self.context)

    @property
    def resources(self):
        resources = []
        project = self.project

        operatives = project.operatives or []
        for operative in operatives:
            if operative.user_id not in resources:
                resources.append(operative.user_id)

        bookings = self.get_bookings(ignore_userid=1)
        for booking in bookings:
            for assignee in booking.assigned_to or []:
                if assignee not in resources:
                    resources.append(assignee)
        res = []
        # resources now contains user ids
        for userid in set(resources):
            details = api.users.get_user_details(
                self.context,
                userid,
                **self.tools)
            details['selected'] = self.request.get('employee') == userid
            res.append(details)
        return res

    @property
    def _date_range(self):
        today = datetime.date.today()
        year = int(self.request.get('year', today.year))
        month = self.request.get('month', today.month)
        if month != 'all':
            month = int(month)
            start_month = stop_month = month
        else:
            start_month = 1
            stop_month = 12
        daylast = calendar.monthrange(year, stop_month)[1]
        from_date = datetime.datetime(year, start_month, 1, 0, 0)
        to_date = datetime.datetime(year, stop_month, daylast, 23, 59)
        return (from_date, to_date)

    def get_bookings(self, date_range=None, ignore_userid=False):
        if date_range is None:
            date_range = self._date_range
        data = dict(
            project=self.context,
            from_date=date_range[0],
            to_date=date_range[1],
        )
        userid = self.request.get('employee', 'all')
        if userid != 'all' and not ignore_userid:
            data['userid'] = userid
        bookings = api.booking.get_bookings(**data)
        return bookings

    def details_report(self):
        total = Decimal('0.0')
        _bookings = []
        for booking in self.get_bookings():
            _bookings.append(AttrDict({
                'date': self.context.toLocalizedTime(booking.date.isoformat()),
                'time': booking.time,
                'url': booking.getURL(),
                'title': booking.Title,
                'user': api.users.get_user_details(
                    self.context,
                    booking.Creator,
                    **self.tools)
            }))
            total += booking.time
        return {
            'bookings': _bookings,
            'total': total
        }

    def _group_by_month(self, bookings):
        res = {}
        for item in bookings:
            month = item.date.month
            weekno = item.date.isocalendar()[1]
            if not month in res:
                res[month] = {weekno: item.time}  # weeks
            else:
                if not weekno in res[month]:
                    res[month][weekno] = item.time
                else:
                    res[month][weekno] += item.time
        return res

    def monthly_report(self):
        bymonth = []
        bookings = self.get_bookings()
        grouped = self._group_by_month(bookings)
        big_total = 0
        for month, weeks in grouped.iteritems():
            month_total = sum(weeks.values())
            big_total += month_total
            bymonth.append({
                'number': month,
                'label': MONTHS[month - 1],
                'total': month_total,
                'weeks': weeks,
            })
        bymonth.sort(key=lambda x: x['number'])
        return {
            'total': big_total,
            'bymonth': bymonth,
        }

    def total_estimated(self):
        return self.project.initial_estimate

    def hour_to_days(self, value):
        """ return formatted time in days for given hour value
        """
        # TODO: handle rounding
        return value / 8
