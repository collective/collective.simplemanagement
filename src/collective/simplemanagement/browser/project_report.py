import datetime
import calendar
from decimal import Decimal

from plone.memoize.view import memoize as view_memoize

from ..utils import get_user_details
from ..utils import get_bookings
from ..utils import get_project
from ..interfaces import IProject

from dashboard import DashboardMixin
from worklog import MONTHS


class ReportView(DashboardMixin):

    @property
    def months(self):
        today = datetime.date.today()
        for i, month in enumerate(MONTHS):
            num = i + 1
            yield {
                'value': num,
                'label': month,
                'selected': int(self.request.get('month', today.month)) == num
            }

    @property
    def years(self):
        today = datetime.date.today()
        for i in xrange(today.year - 2, today.year + 1):
            yield {
                'value': i,
                'label': i,
                'selected': int(self.request.get('year', today.year)) == i
            }

    @property
    @view_memoize
    def project(self):
        return get_project(self.context)

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
            details = get_user_details(self.context,
                                       userid,
                                       **self.tools)
            details['selected'] = self.request.get('employee') == userid
            res.append(details)
        return res

    @property
    def _date_range(self):
        today = datetime.date.today()
        month = int(self.request.get('month', today.month))
        year = int(self.request.get('year', today.year))
        daylast = calendar.monthrange(year, month)[1]
        from_date = datetime.datetime(year, month, 1, 0, 0)
        to_date = datetime.datetime(year, month, daylast, 23, 59)
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
        bookings = get_bookings(**data)
        return bookings

    def details_report(self):
        total = Decimal('0.0')
        _bookings = []
        for booking in self.get_bookings():
            _bookings.append({
                'date': self.context.toLocalizedTime(booking.date.isoformat()),
                'time': booking.time,
                'url': booking.getURL(),
                'title': booking.Title,
                'user': get_user_details(self.context,
                                         booking.Creator,
                                         **self.tools)
            })
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
        res = []
        today = datetime.date.today()
        year = int(self.request.get('year', today.year))
        from_date = datetime.date(year, 1, 31)
        to_date = datetime.date(year, 12, 31)
        bookings = self.get_bookings(date_range=(from_date, to_date))
        grouped = self._group_by_month(bookings)
        for month, weeks in grouped.iteritems():
            month_total = sum(weeks.values())
            res.append({
                'number': month,
                'label': MONTHS[month - 1],
                'total': month_total,
                'weeks': weeks,
            })
        res.sort(key=lambda x: x['number'])
        return res
