import json, calendar
from decimal import Decimal
from datetime import datetime, date, time, timedelta

from zope.interface import implements
from zope.component import getUtility
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import IPublishTraverse, NotFound
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize as instance_memoize

from ..interfaces import IBookingHoles, IProject
from ..configure import ONE_DAY, ONE_WEEK, Settings
from ..utils import (AttrDict, datetimerange, get_user_details,
                     get_difference_class, quantize, get_project, get_story)


class WorklogBackend(BrowserView):

    implements(IPublishTraverse)

    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self, context, request):
        super(WorklogBackend, self).__init__(context, request)
        self.resource_id = None
        self.date = None

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

    def publishTraverse(self, request, name):
        if self.resource_id is None:
            self.resource_id = name
        elif self.date is None:
            self.date = datetime.strptime(name, "%Y-%m-%d").date()
        else:
            raise NotFound(self, name, request)
        return self

    def resources(self):
        settings = Settings()
        if IProject.providedBy(self.context):
            bookings = self.tools.portal_catalog.searchResults({
                'path': '/'.join(self.context.getPhysicalPath()),
                'portal_type': 'Booking'
            })
            resources = [ o.user_id for o in self.context.operatives ]
            for booking in bookings:
                if booking.assigned_to not in resources:
                    resources.append(booking.assigned_to)
        else:
            group = self.tools.portal_groups.getGroupById(
                settings.employees_group
            )
            if group is not None:
                resources = group.getMemberIds()
            else:
                resources = []
        for resource in resources:
            yield get_user_details(self.context, resource, **self.tools)

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
        start = start - timedelta(days=((settings.monthly_weeks_before-1)*7))
        month_end = date(year, month, 1) + timedelta(days=month_length)
        end = month_end + timedelta(days=(7-month_end.weekday()))
        end = end + timedelta(days=((settings.monthly_weeks_after-1)*7))
        return (
            (previous_year, previous_month),
            (start, end),
            (next_year, next_month)
        )

    def get_bookings_and_holes(self, date_, resource, booking_holes):
        bookings_ = self.tools.portal_catalog.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Booking',
            'assigned_to': resource,
            'booking_date': DateTime(date_.strftime("%Y-%m-%d"))
        })
        holes = booking_holes.iter_user(
            resource,
            datetime.combine(date_, time(0)),
            datetime.combine(date_ + ONE_DAY, time(0))
        )
        return (bookings_, holes)

    def monthly_bookings(self):
        settings = Settings()
        booking_holes = getUtility(IBookingHoles)
        resources = self.request.get(
            'resources',
            [ r['user_id'] for r in self.resources() ]
        )
        previous, (start, end), next = self.get_month_data(settings)
        total_hours = {}
        for week_start, week_end in datetimerange(start, end, ONE_WEEK):
            week_identifier = '%s - %s' % (
                week_start.strftime("%d/%m"),
                (week_end-ONE_DAY).strftime("%d/%m")
            )
            week_hours = total_hours.setdefault(week_identifier, [])
            for date_, __ in datetimerange(week_start, week_end, ONE_DAY):
                day_hours = []
                for resource in resources:
                    bookings_, holes = self.get_bookings_and_holes(
                        date_,
                        resource,
                        booking_holes
                    )
                    total = reduce(
                        lambda x, y: x + y,
                        [ b.time for b in bookings_ ],
                        Decimal("0.00")
                    )
                    total = reduce(
                        lambda x, y: x + y,
                        [ h.hours for h in holes ],
                        total
                    )
                    day_hours.append((
                        resource,
                        {
                            'total': str(quantize(total)),
                            # TODO: the class here should also depend
                            # on whether the day is working day or not,
                            # which includes checking weekends AND holidays
                            'class': get_difference_class(
                                settings.man_day_hours,
                                total,
                                settings=settings
                            ),
                            'href': '%s/%s/%s' % (
                                self.request['URL'],
                                resource,
                                date_.strftime("%Y-%m-%d")
                            )
                        }
                    ))
                week_hours.append(day_hours)
        return json.dumps({
            'previous': '%s-%s' % previous,
            'next': '%s-%s' % next,
            'total_hours': total_hours
        })

    def booking_details(self):
        booking_holes = getUtility(IBookingHoles)
        bookings_, holes = self.get_bookings_and_holes(
            self.date,
            self.resource_id,
            booking_holes
        )
        booking_details = []
        for booking in bookings_:
            booking = booking.getObject()
            booking_details.append({
                'type': 'booking',
                'project': get_project(booking).title,
                'story': get_story(booking).title,
                'hours': str(quantize(booking.time))
            })
        booking_details.extend(
            [ { 'type': 'hole', 'reason': h.reason,
                'hours': str(quantize(h.hours)) } for h in holes ]
        )
        return json.dumps(booking_details)

    def __call__(self):
        self.request.response.setHeader("Content-type", "application/json")
        if self.resource_id is not None and self.date is not None:
            return self.booking_details()
        return self.monthly_bookings()
