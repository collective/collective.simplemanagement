import datetime

from zope.security import checkPermission
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize as instance_memoize
from plone.uuid.interfaces import IUUID

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.Poi.browser.tracker import ACTIVE_STATES as TICKETS_ACTIVE_STATES

from ..configure import Settings
from ..interfaces import IUserStoriesListing
from ..interfaces import IProject
from ..utils import AttrDict
from .. import api


class DashboardMixin(BrowserView):

    @property
    def is_project(self):
        return IProject.providedBy(self.context)

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
                'UID': IUUID(prj),
                'priority': prj.priority,
                'title': prj.Title(),
                'description': prj.Description(),
                'url': prj.absolute_url(),
            }

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    def _get_employee_filter(self):
        if self.user_can_manage_project:
            user_id = self.request.get('employee', self.user.getId())
        else:
            user_id = self.user.getId()
        return user_id

    def can_add_booking(self):
        return checkPermission('simplemanagement.AddBooking', self.context)


class TicketsMixIn(object):

    n_tickets = 0

    def employee_details(self):
        employee = self.request.get('employee')
        if not employee:
            return False
        else:
            return api.users.get_user_details(
                self.context, employee, **self.tools)

    def employees(self):
        if IProject.providedBy(self.context):
            # TODO: filter user by context
            pass
        resources = api.users.get_employee_ids(self.context)
        for resource in resources:
            if resource != self.user.getId():
                yield api.users.get_user_details(
                    self.context, resource, **self.tools)

    def _get_tickets(self):
        pc = self.tools['portal_catalog']
        user_id = self._get_employee_filter()

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
            'modified': item.modified,
            'severity': item.getSeverity,
            'review_state': api.content.get_wf_state_info(item, self.context),
            'project': self.get_project_details(item)
        }

    def tickets(self):
        projects = {}
        for item in self._get_tickets():
            ticket = self._format_ticket(item)
            prj = ticket.pop('project')
            if not projects.get(prj['UID']):
                projects[prj['UID']] = prj
                projects[prj['UID']]['tickets'] = []
            projects[prj['UID']]['tickets'].append(ticket)
        projects = [p[1] for p in projects.items()]
        projects.sort(key=lambda x: x['priority'])

        return projects

    def timeago(self, timestamp):
        return api.date.timeago(timestamp.utcdatetime())


class DashboardView(DashboardMixin, TicketsMixIn):

    trackers_forlder_id = 'trackers'

    def __init__(self, context, request):
        super(DashboardMixin, self).__init__(context, request)
        if not self.is_project:
            request.set('disable_border', 1)

    def projects(self):
        projects = {}
        project_states = ['development', 'maintenance']
        if self.request.form.get('planning') == 'on':
            project_states.extend(['offer', 'planning'])
        story_states = ['in_progress']
        listing = IUserStoriesListing(self.context)(
            user_id=self._get_employee_filter(),
            project_states=project_states,
            story_states=story_states,
            project_info=True
        )
        for st in listing.stories:
            prj = st.pop('project')
            if prj['UID'] not in projects:
                projects[prj['UID']] = prj
                projects[prj['UID']]['stories'] = []

            projects[prj['UID']]['stories'].append(st)
        projects = [p[1] for p in projects.items()]
        projects.sort(key=lambda x: x['priority'])
        return projects

    def bookings(self):
        user_id = self._get_employee_filter()
        project = None
        is_project_context = IProject.providedBy(self.context)
        if is_project_context:
            project = self.context

        from_date = datetime.date.today() - datetime.timedelta(days=30)
        _bookings = api.booking.get_bookings(
            user_id,
            project=project,
            from_date=from_date
        )
        results = []
        for booking in _bookings:
            helpers = getMultiAdapter((booking, self.request), name='helpers')
            results.append(helpers.info())
        return results

    def trackers(self):
        """ get global generic trackers
        from `trackers` folder, if any.
        """
        if not base_hasattr(self.context, self.trackers_forlder_id):
            return []
        trackers_folder = getattr(self.context, self.trackers_forlder_id)
        pc = self.tools['portal_catalog']
        query = {
            'portal_type': 'PoiTracker',
            'sort_on': 'modified',
            'sort_order': 'descending',
            'path': '/'.join(trackers_folder.getPhysicalPath())
        }
        results = pc.searchResults(query)
        return results

    def my_issues_search_url(self):
        """ get relative search url for tickets assigned to current user.
        """
        url = ''.join([
            'poi_issue_search?state=',
            '&amp;state='.join(TICKETS_ACTIVE_STATES),
            '&amp;responsible=%s' % self.user.getId()
        ])
        return url
