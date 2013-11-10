#-*- coding: utf-8 -*-

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import csv
import datetime

from Products.Five.browser import BrowserView

CTYPES = {
    '.csv': 'text/csv'
}


class Mixin(BrowserView):
    """ base klass for exports
    """

    filename_prefix = 'export-'
    filename_ext = '.csv'

    def __call__(self):
        return self.export()

    @property
    def filename(self):
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        fname = self.filename_prefix + now + self.filename_ext
        return fname

    def export(self):
        """ Export users within CSV file.
        """
        data = self.get_data()
        self._prepare_response(data, self.filename)
        return data

    def _prepare_response(self, data, filename):
        """ prepare response headers
        """
        response = self.request.response
        response.addHeader('Content-Disposition', "attachment; filename=%s" % filename)
        response.addHeader('Content-Type', CTYPES[self.filename_ext])
        response.addHeader('Content-Length', "%d" % len(data))
        response.addHeader('Pragma', "no-cache")
        response.addHeader('Cache-Control', "must-revalidate, post-check=0, pre-check=0, public")
        response.addHeader('Expires', "0")


class ExportCSV(Mixin):
    """ base klass for CSV exports
    """

    header = ()

    def get_data(self):
        """ Write header + lines within the CSV file """
        datafile = StringIO()
        writer = csv.writer(datafile)
        header = self.get_header()
        writer.writerow(header)
        lines = self.get_lines()
        map(writer.writerow, lines)
        data = datafile.getvalue()
        datafile.close()
        return data

    def get_header(self):
        return self.header

    def get_lines(self):
        """ return csv lines as iterator
        """
        raise NotImplementedError("please, provide a 'process' method!")
