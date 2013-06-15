import datetime
import calendar

from ..utils import get_user_details
from ..utils import get_bookings
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
    def resources(self):
        operatives = self.context.operatives or []
        for operative in operatives:
            details = get_user_details(self.context,
                                       operative.user_id,
                                       **self.tools)
            details['selected'] = self.request.get('employee') == operative.user_id
            yield details

    @property
    def _date_range(self):
        today = datetime.date.today()
        month = int(self.request.get('month', today.month))
        year = int(self.request.get('year', today.year))
        daylast = calendar.monthrange(year, month)[1]
        from_date = datetime.datetime(year, month, 1, 0, 0)
        to_date = datetime.datetime(year, month, daylast, 23, 59)
        return (from_date, to_date)

    def bookings(self):
        userid = self.request.get('employee', 'all')
        project = None
        is_project_context = IProject.providedBy(self.context)
        if is_project_context:
            project = self.context

        data = dict(
            project=project,
            from_date=self._date_range[0],
            to_date=self._date_range[1],
        )
        if userid != 'all':
            data['userid'] = userid
        bookings = get_bookings(**data)
        results = []
        for booking in bookings:
            results.append({
                'date': self.context.toLocalizedTime(booking.date.isoformat()),
                'time': booking.time,
                'url': booking.getURL(),
                'title': booking.Title,
                'user': get_user_details(self.context,
                                         booking.Creator,
                                         **self.tools)
            })
        return results
