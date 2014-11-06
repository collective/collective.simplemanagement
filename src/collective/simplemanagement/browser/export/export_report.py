#-*- coding: utf-8 -*-

from .tocsv import ExportCSV

from ..project_report import ProjectReportView


class ExportReportCSV(ExportCSV, ProjectReportView):
    """  export @@report view results to CSV
    """

    filename_prefix = 'export-report-'
    header = ('data', 'log', 'impiegato', 'ore')

    def get_lines(self):
        result = self.details_report()
        for item in result['bookings']:
            yield (
                item.date,
                item.title,
                item.user.fullname,
                item.time,
            )
