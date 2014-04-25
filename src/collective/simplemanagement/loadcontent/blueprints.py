import logging
import re
from datetime import date, timedelta

from zope.interface import directlyProvides
from zope.interface import implementer
from zope.component import getUtility

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.simplemanagement.interfaces import IBookingStorage

from ..structures import Resource
from ..structures import Environment
from ..structures import Milestone

logger = logging.getLogger(__name__)


def unicodize(val):
    if isinstance(val, unicode):
        return val
    return val.decode('utf-8')


@implementer(ISection)
class SetElementsMixIn(object):

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous

    def transform(self, value):
        raise NotImplementedError

    def __iter__(self):
        for item in self.previous:
            if not item.get(self._key):
                yield item
                continue

            item[self._key] = self.transform(item[self._key])
            yield item


@implementer(ISection)
class BookingConstructor(object):

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.storage = getUtiity(IBookingStorage)

    def __iter__(self):
        for item in self.previous:
            if not item.get(self._key):
                yield item
                continue

            item[self._key] = self.transform(item[self._key])
            yield item


class SetOperatives(SetElementsMixIn):
    _key = 'operatives'

    def create_operative(self, value):
        res = Resource()
        res.role = value[0]
        res.user_id = unicodize(value[1])
        return res

    def transform(self, value):
        value = eval(value)
        return [self.create_operative(i) for i in value]


directlyProvides(SetOperatives, ISectionBlueprint)


@implementer(ISection)
class SetEnvironments(SetElementsMixIn):
    _key = 'environments'

    def create_environment(self, value):
        res = Environment()
        res.name = value[0]
        res.env_type = value[1]
        res.url = value[2]
        return res

    def transform(self, value):
        value = eval(value)
        return [self.create_environment(i) for i in value]


directlyProvides(SetEnvironments, ISectionBlueprint)


@implementer(ISection)
class SetMilestones(SetElementsMixIn):
    _key = 'milestones'

    def create_milestone(self, value):
        res = Milestone()
        res.name = value[0]
        res.status = value[1]
        return res

    def transform(self, value):
        value = eval(value)
        return [self.create_milestone(i) for i in value]

directlyProvides(SetMilestones, ISectionBlueprint)


DATE_REGEX = re.compile(
    r'^(?P<sign>\+|-)(?P<value>[0-9]+)(?P<quantifier>[dw])$'
)


@implementer(ISection)
class ConvertDate(object):

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self._key = options['key'].strip()

    def transform(self, value):
        today = date.today()
        values = DATE_REGEX.match(value).groupdict()
        delta_value = int(values['value'])
        if values['quantifier'] == 'd':
            delta = timedelta(days=delta_value)
        elif values['quantifier'] == 'w':
            delta = timedelta(days=(delta_value * 7))
        if values['sign'] == '+':
            return today + delta
        else:
            return today - delta

    def __iter__(self):
        for item in self.previous:
            if not item.get(self._key):
                yield item
                continue

            item[self._key] = self.transform(item[self._key])
            yield item

directlyProvides(ConvertDate, ISectionBlueprint)
