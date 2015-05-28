#-*- coding: utf-8 -*-
from decimal import Decimal
from Products.CMFCore.utils import getToolByName
from collective.simplemanagement.api.booking import get_timings
from collective.simplemanagement.utils import quantize
from .tocsv import ExportCSV


class ExportProjectsReportCSV(ExportCSV):
    """  export @@projects-report-csv view results to CSV
    """

    filename_prefix = 'projects-report-'
    header = ('name', 'link', 'review_state', 'start', 'estimate_end',
              'effective_end', 'budget_days', 'effective_days', 'bookings')

    default_query = {
        'portal_type': 'Project',
        'sort_on': 'modified',
        'sort_order': 'reverse',
    }

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def date_isoformat(self, date):
        return self.context.toLocalizedTime(date.isoformat())

    def get_lines(self):
        projects = self.catalog(**self.default_query)
        zero = Decimal('0.00')
        for project in projects:
            obj = project.getObject()
            timings = get_timings(obj)
            estimate = (timings['estimate'] > 0) and timings['estimate'] or zero
            bookings = (timings['resource_time'] > 0) and timings['resource_time'] or zero
            start_date = obj.prj_start_date and self.date_isoformat(
                obj.prj_start_date) or None
            expected_end_date = obj.prj_expected_end_date and self.date_isoformat(
                obj.prj_expected_end_date) or None
            end_date = obj.prj_end_date and self.date_isoformat(
                obj.prj_end_date) or None

            yield (
                project.Title,
                project.getURL(),
                project.review_state,
                start_date,
                expected_end_date,
                end_date,
                obj.budget,
                quantize(estimate),
                quantize(bookings)
            )
