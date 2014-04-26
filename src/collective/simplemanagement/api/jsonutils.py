import json
from decimal import Decimal
from datetime import time
from datetime import date
from datetime import datetime
from DateTime import DateTime


class ExtendedJSONEncoder(json.JSONEncoder):

    DATE_RFC822_FORMAT = '%a, %d %b %Y'
    TIME_RFC822_FORMAT = '%H:%M:%S'

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, DateTime):
            return obj.rfc822()
        elif isinstance(obj, date):
            return obj.strftime(self.DATE_RFC822_FORMAT)
        elif isinstance(obj, time):
            return obj.strftime(self.TIME_RFC822_FORMAT)
        elif isinstance(obj, datetime):
            return obj.strftime(
                self.DATE_RFC822_FORMAT + ' ' + self.TIME_RFC822_FORMAT + ' %z'
            )
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def jsonmethod(encoder=ExtendedJSONEncoder):
    def decorator(meth):
        def wrapper(self, *args, **kwargs):
            result = meth(self, *args, **kwargs)
            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(result, cls=encoder)
        return wrapper
    return decorator
