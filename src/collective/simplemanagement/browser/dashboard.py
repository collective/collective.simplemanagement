import datetime

from zope.security import checkPermission

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
from ..utils import get_wf_state_info
from ..utils import get_employee_ids
from ..utils import get_user_details
from ..utils import get_project


class DashboardMixin(BrowserView):

    @property
    @instance_memoize
    def tools(self):
        return AttrDict({
            'portal_catalog': getToolByName(self.context, 'portal_catalog'),
            'portal_membership': getToolByName(
                self.context,
                'portal_membership'
            ),
            'portal_url': getToolByName(self.context, 'portal_url'),
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

    def get_project_details(self, brain):
        # we can't use utils.get_project because
        # PoiIssue doesn't provide ILocation
        prj = None
        context = brain.getObject()
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

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )


class TicketsMixIn(object):

    n_tickets = 0

    def employee_details(self):
        employee = self.request.get('employee')
        if not employee:
            return False
        else:
            return get_user_details(self.context, employee, **self.tools)

    def employees(self):
        if IProject.providedBy(self.context):
            # TODO: filter user by context
            pass
        resources = get_employee_ids(self.context)
        for resource in resources:
            if resource != self.user.getId():
                yield get_user_details(self.context, resource, **self.tools)

    def _get_tickets(self):
        pc = self.tools['portal_catalog']
        if self.user_can_manage_project:
            user_id = self.request.get('employee', self.user.getId())
        else:
            user_id = self.user.getId()

        query = {
            'portal_type': 'PoiIssue',
            'getResponsibleManager': user_id,
            'review_state': ('new', 'open', 'in-progress', 'unconfirmed'),
            'sort_on': 'modified',
            'sort_order': 'descending'
        }

        if IProject.providedBy(self.context):
            query['path'] = '/'.join(self.context.getPhysicalPath())

        results = pc.searchResults(query)
        self.n_tickets = len(results)
        return results

    def _format_ticket(self, item):
        return {
            'url': item.getURL(),
            'title': item.Title,
            'id': item.getId,
            'created': item.created,
            'modified': item.modified,
            'severity': item.getSeverity,
            'review_state': get_wf_state_info(item, self.context),
            'project': self.get_project_details(item)
        }

    def tickets(self):
        return [self._format_ticket(item) for item in self._get_tickets()]

    def timeago(self, timestamp):
        return timeago(timestamp.utcdatetime())


class DashboardView(DashboardMixin, TicketsMixIn):

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
