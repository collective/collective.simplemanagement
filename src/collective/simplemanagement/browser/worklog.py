import json
import calendar
import plone.api
from decimal import Decimal
from datetime import datetime, date, timedelta

from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import IPublishTraverse, NotFound
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize as instance_memoize

from .. import api
from .. import messageFactory as _ # noqa
from ..interfaces import IProject
from ..configure import ONE_DAY, ONE_WEEK, Settings

from ..utils import AttrDict, quantize
from .widgets import book_widget


MONTHS = (
    _(u"January"),
    _(u"February"),
    _(u"March"),
    _(u"April"),
    _(u"May"),
    _(u"June"),
    _(u"July"),
    _(u"August"),
    _(u"September"),
    _(u"October"),
    _(u"November"),
    _(u"December")
)


class WorklogBase(BrowserView):

    @property
    @instance_memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog'),
            'portal_membership': getToolByName(self.context,
                                               'portal_membership'),
            'portal_url': getToolByName(self.context, 'portal_url'),
            'portal_groups': getToolByName(self.context, 'portal_groups')
        })

    @property
    def current_user_id(self):
        return plone.api.user.get_current().getUserName()

    def resources(self):
        resources = []
        if IProject.providedBy(self.context):
            operatives = self.context.operatives or []
            for operative in operatives:
                if operative.user_id not in resources:
                    resources.append(operative.user_id)

            bookings = api.booking.get_bookings(project=self.context)
            for booking in bookings:
                assignee = booking.owner
                if assignee not in resources:
                    resources.append(assignee)
        else:
            resources = api.users.get_employee_ids(self.context)

        # add current user id
        current_user_id = self.current_user_id
        if current_user_id not in resources:
            resources.append(current_user_id)

        for resource in resources:
            yield api.users.get_user_details(
                self.context, resource, **self.tools)


class Worklog(WorklogBase):

    def js_init(self, id):
        return """
        (function($) {{
            $(window).load(function() {{
                window.simplemanagement.worklog.make('{id}');
            }});
        }})(jQuery);
        """.format(id=id)

    def json_resources(self):
        resources = {}
        for resource in self.resources():
            resources[resource['user_id']] = resource
        return json.dumps(resources)


class WorklogBackend(WorklogBase):

    implements(IPublishTraverse)

    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, context, request):
        super(WorklogBackend, self).__init__(context, request)
        self.resource_id = None
        self.date = None

    def publishTraverse(self, request, name): # noqa
        if self.resource_id is None:
            self.resource_id = name
        elif self.date is None:
            self.date = datetime.strptime(name, "%Y-%m-%d").date()
        else:
            raise NotFound(self, name, request)
        return self

    def get_month_data(self, settings):
        # TODO: maybe this should live elsewhere
        today = date.today()
        year, month = self.request.form.get(
            'month',
            today.strftime('%Y-%m')
        ).split('-')
        month, year = int(month), int(year)
        previous_month = month - 1
        previous_year = year
        if previous_month == 0:
            previous_month = 12
            previous_year = year - 1
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year = year + 1
        month_start, month_length = calendar.monthrange(year, month)
        start = date(year, month, 1) - timedelta(days=month_start)
        start = start - \
            timedelta(days=((settings.monthly_weeks_before - 1) * 7))
        month_end = date(year, month, 1) + timedelta(days=month_length)
        end = month_end + timedelta(days=(7 - month_end.weekday()))
        end = end + timedelta(days=((settings.monthly_weeks_after - 1) * 7))
        return (
            (start, end),
            (previous_year, previous_month),
            (year, month),
            (next_year, next_month)
        )

    def get_bookings(self, date_, resource):
        bookings = api.booking.get_bookings(
            project=self.context,
            userid=resource,
            date=date_
        )
        return bookings

    def monthly_bookings(self):
        settings = Settings()
        # by default we display current user data
        resources = self.request.get(
            'resources',
            self.current_user_id
        )

        if isinstance(resources, str):
            resources = [resources]
        (start, end), previous, current, next = self.get_month_data(settings)
        total_hours = []
        _translate = lambda x: self.context.translate(x)
        drange = api.date.datetimerange(start, end, ONE_WEEK)
        for week_start, week_end in drange:
            week_identifier = u'<i>%d %s</i> &mdash; <i>%d %s</i>' % (
                week_start.day,
                _translate(MONTHS[week_start.month - 1]),
                (week_end - ONE_DAY).day,
                _translate(MONTHS[(week_end - ONE_DAY).month - 1])
            )
            week_hours = []
            for resource in resources:
                day_hours = []
                drange = api.date.datetimerange(week_start,
                                                week_end,
                                                ONE_DAY)
                for date_, __ in drange:
                    bookings_ = self.get_bookings(date_, resource)

                    total = reduce(
                        lambda x, y: x + y,
                        [b.time for b in bookings_],
                        Decimal("0.00")
                    )
                    day_hours.append({
                        'total': str(quantize(total)),
                        # TODO: the class here should also depend
                        # on whether the day is working day or not,
                        # which includes checking weekends AND holidays
                        'class': api.booking.get_difference_class(
                            settings.man_day_hours,
                            total,
                            settings=settings
                        ),
                        'href': '%s/%s/%s' % (
                            self.request['URL'],
                            resource,
                            date_.strftime("%Y-%m-%d")
                        )
                    })
                week_hours.append((resource, day_hours))
            total_hours.append((week_identifier, week_hours))
        return json.dumps({
            'previous': {
                'value': '%s-%s' % previous,
                'title': u'%s %d' % (_translate(MONTHS[previous[1] - 1]),
                                     previous[0])
            },
            'current': {
                'value': '%s-%s' % current,
                'title': u'%s <small>%d</small>' % (
                    _translate(MONTHS[current[1] - 1]),
                    current[0])
            },
            'next': {
                'value': '%s-%s' % next,
                'title': u'%s %d' % (_translate(MONTHS[next[1] - 1]), next[0])
            },
            'total_hours': total_hours
        })

    def booking_details(self):
        bookings_ = self.get_bookings(
            self.date,
            self.resource_id
        )
        booking_details = []
        for booking in bookings_:
            project = api.booking.get_project(booking)
            project_title = ''
            project_url = ''
            if project:
                project_title = project.title
                project_url = project.absolute_url()
            story = api.booking.get_story(booking)
            story_title = ''
            story_url = ''
            if story:
                story_title = story.title
                story_url = story.absolute_url()
            booking_details.append({
                'type': 'booking',
                'project': project_title,
                'project_url': project_url,
                'story': story_title,
                'story_url': story_url,
                'booking': book_widget.format_text(booking, drop_chars=['@']),
                'hours': str(quantize(booking.time))
            })
        return json.dumps(booking_details)

    def __call__(self):
        self.request.response.setHeader("Content-type", "application/json")
        if self.resource_id is not None and self.date is not None:
            return self.booking_details()
        return self.monthly_bookings()
