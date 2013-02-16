import datetime

from plone.memoize.instance import memoize as instance_memoize
from plone.memoize.view import memoize as view_memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from ..configure import Settings
from ..interfaces import IMyStoriesListing
from ..interfaces import IProject
from ..utils import timeago
from ..utils import AttrDict
from ..utils import get_bookings
from ..utils import get_booking_holes


class DashboardMixin(BrowserView):

    @property
    @instance_memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog')
        })

    @property
    @instance_memoize
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')

    @property
    def user(self):
        user = None
        portal_state = self.portal_state
        if not portal_state.anonymous():
            user = portal_state.member()
        return user

    @property
    @instance_memoize
    def settings(self):
        return Settings()


class MyTickets(DashboardMixin):

    @property
    def _query(self):
        return {
            'portal_type': 'PoiIssue',
            'getResponsibleManager': self.user.getId(),
            'review_state': ('new', 'open', 'in-progress', 'unconfirmed'),
            'sort_on': 'modified',
            'sort_order': 'descending'
        }
        # 'resolved',

    def tickets(self):
        pc = self.tools['portal_catalog']
        tickets = pc.searchResults(self._query)
        return tickets

    def timeago(self, timestamp):
        return timeago(timestamp.utcdatetime())

    def get_project(self, brain):
        context = brain.getObject()
        prj = None
        while context is not None:
            if IProject.providedBy(context):
                prj = context
                break
            try:
                context = context.__parent__
            except AttributeError:
                break

        if prj:
            return {
                'title': prj.Title(),
                'description': prj.Description(),
                'url': prj.absolute_url(),
            }


class MyStories(DashboardMixin):
    pass


class DashboardView(DashboardMixin):

    def projects(self):
        listing = IMyStoriesListing(self.context)
        projects = {}
        for st in listing.stories(project_info=True):
            prj = st.pop('project')
            if prj['UID'] not in projects:
                projects[prj['UID']] = prj
                projects[prj['UID']]['stories'] = []

            projects[prj['UID']]['stories'].append(st)

        projects = [p[1] for p in projects.items()]
        projects.sort(key=lambda x: x['priority'])
        return projects

    @property
    def hole_reasons(self):
        return self.settings.off_duty_reasons

    @property
    @view_memoize
    def hole_settings(self):
        start_delta = self.settings.booking_check_delta_days_start
        end_delta = self.settings.booking_check_delta_days_end
        today = datetime.date.today()
        from_date = today - datetime.timedelta(start_delta)
        to_date = today - datetime.timedelta(end_delta)
        return AttrDict({
            'from_date': from_date,
            'to_date': to_date,
            'warning_delta_percent': self.settings.warning_delta_percent,
            'man_day_hours': self.settings.man_day_hours,
        })

    # @view_memoize
    def bookings(self, userid, from_date, to_date):
        cat = self.tools.portal_catalog
        bookings = get_bookings(
            userid=userid,
            portal_catalog=cat,
            from_date=from_date,
            to_date=to_date
        )
        return bookings

    def booking_holes(self):
        member = self.portal_state.member()
        userid = member.getId()
        hole_settings = self.hole_settings
        man_day_hours = hole_settings.man_day_hours
        expected_working_time = man_day_hours - \
            (man_day_hours * hole_settings.warning_delta_percent)
        from_date = hole_settings.from_date
        to_date = hole_settings.to_date
        bookings = self.bookings(userid, from_date, to_date)
        holes = get_booking_holes(userid, bookings,
                                  expected_working_time=expected_working_time,
                                  man_day_hours=man_day_hours,
                                  from_date=from_date, to_date=to_date)
        return holes
