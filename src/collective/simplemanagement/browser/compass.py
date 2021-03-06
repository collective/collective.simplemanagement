import json
import plone.api
from copy import deepcopy
from datetime import date
from datetime import datetime
from decimal import Decimal
from DateTime import DateTime
from AccessControl import Unauthorized
from zope.component import getUtility
from zope.security import checkPermission
from zope.schema.interfaces import IVocabularyFactory
from plone.registry.interfaces import IRegistry
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..interfaces.settings import ISettings
from ..interfaces.compass import ICompassSettings
from .. import api
from ..structures import Resource
from ..configure import DAY_HOURS
from .. import messageFactory as _

# Validate both on the server and client side,
# using z3c.form on the client se in a less stressful way

format_booking_value = lambda x: round(x / DAY_HOURS, 1)
PRJ_URL_TEMPLATE = "{0}/report?month={1}&tab=synoptic&year={2}"
USR_URL_TEMPLATE = "{0}/dashboard?employee={1}"


def get_bookings(start, end):
    end = datetime(end.year, end.month, end.day, 23, 59, 59)
    start = datetime(start.year, start.month, start.day, 0, 0, 0)
    bookings = api.booking.get_bookings(from_date=start, to_date=end)
    results = {}
    for item in bookings:
        if item.project is None:
            # we need project's booking, skip this
            continue
        uid = item.project
        if not uid in results:
            results[uid] = {}
        creator = item.owner
        if creator not in results[uid]:
            results[uid][creator] = 0
        results[uid][creator] += item.time
    return results


class CompassMixIn(object):
    pass


class History(api.views.Traversable, CompassMixIn):

    STEP = 20  # Used for pagination/infinite scroll

    template = ViewPageTemplateFile('templates/compass_history.pt')

    def __init__(self, context, request):
        super(History, self).__init__(context, request)
        self.tools = api.portal.LazyTools(context)
        self.key = None
        self.data = None

    def get_employees(self, project, employees):
        for employee in project.get('people', []):
            employee_id = employee.get('id')
            if employee_id:
                user_details = api.users.get_user_details(
                    self.context,
                    employee_id,
                    portal_url=self.tools['portal_url'],
                    portal_membership=self.tools['portal_membership']
                )
                if user_details:
                    data = employees.setdefault(employee_id, {})
                    data['name'] = user_details['fullname']
                    projects = data.setdefault('projects', [])
                    if not project['uid'] in projects:
                        projects.append(project['uid'])
                    data['total_effort'] = (
                        data.get('total_effort', 0.0) +
                        float(employee.get('effort', u'0.0'))
                    )
                    data['booking'] = round(
                        data.get('booking', 0.0) +
                        employee.get('booking', 0.0),
                        1
                    )

    def get_data(self):
        data = deepcopy(self.data)

        portal = plone.api.portal.get()
        portal_url = portal.absolute_url()
        start = data.get('plan_start')
        end = data.get('plan_end')
        if not (start and end):
            return data
        data['plan_end'] = api.date.format(end)
        data['plan_start'] = api.date.format(start)
        data['employees'] = {}

        bookings = get_bookings(start, end)
        i = 1
        for prj in data['projects']:
            i += 1
            if 'uid' in prj:
                prj_uid = prj['uid']
                project = uuidToObject(prj['uid'])
            else:
                try:
                    project = portal.restrictedTraverse(prj['id'].encode())
                    prj_uid = IUUID(project)
                except:
                    project = None
                    prj_uid = None
            if project is None:
                prj['disabled'] = True
                continue
            else:
                prj['disabled'] = False
            prj_bookings = bookings.pop(prj_uid, {})
            prj['uid'] = prj_uid
            prj['url'] = PRJ_URL_TEMPLATE.format(
                project.absolute_url(),
                start.month,
                start.year
            )
            for employee in prj['people']:
                b = prj_bookings.pop(employee['id'], 0)
                employee['booking'] = format_booking_value(b)
                employee['url'] = USR_URL_TEMPLATE.format(
                    portal_url,
                    employee['id']
                )

            if prj_bookings:
                # Add extra employee
                for k, v in prj_bookings.items():
                    prj['people'].append({
                        'booking': format_booking_value(v),
                        'effort': u'0',
                        'id': k,
                        'is_critical': False,
                        'is_free': False,
                        'role': u''
                    })
            self.get_employees(prj, data['employees'])
        if bookings:
            # add extra projects
            for k, people in bookings.items():
                obj = uuidToObject(k)
                if obj is None:
                    continue
                pw = self.tools['portal_workflow']
                status = pw.getStatusOf("project_workflow", obj)
                new_prj = {
                    'disabled': False,
                    'uid': k,
                    'id': '/'.join(obj.getPhysicalPath()),
                    'name': obj.title_or_id(),
                    'status': status['review_state'],
                    'customer': obj.customer,
                    'priority': obj.priority,
                    'css_class': 'status-indicator state-{}'.format(
                        status['review_state']),
                    'url': PRJ_URL_TEMPLATE.format(
                        obj.absolute_url(),
                        start.month,
                        start.year
                    ),
                    'notes': '',
                    'effort': 0,
                    'active': False,
                    'people': []
                }

                for username, value in people.items():
                    new_prj['people'].append({
                        'booking': format_booking_value(value),
                        'effort': u'0',
                        'id': username,
                        'is_critical': False,
                        'is_free': False,
                        'role': u'',
                        'url': USR_URL_TEMPLATE.format(
                            portal_url,
                            username
                        )
                    })
                data['projects'].append(new_prj)
                self.get_employees(new_prj, data['employees'])

        data['employees'] = json.dumps(data['employees'])
        data['current_user'] = ''
        if not plone.api.user.is_anonymous():
            current = plone.api.user.get_current().getUserName()
            if current in data['employees']:
                data['current_user'] = current
        return data

    def get_effort_classes(self, person_data):
        klasses = ['effort']
        if person_data.get('is_critical'):
            klasses.append('critical')
        elif person_data.get('is_free'):
            klasses.append('free')
        return ' '.join(klasses)

    def augment_user_data(self, data):
        """Augments the user data
        """
        user_id = data.get('id')
        if user_id:
            data['name'] = user_id
            data['avatar'] = ''
            user_details = api.users.get_user_details(
                self.context,
                user_id,
                portal_url=self.tools['portal_url'],
                portal_membership=self.tools['portal_membership']
            )
            if user_details:
                data['name'] = user_details['fullname']
                data['avatar'] = user_details['portrait']
        return data

    def html_notes(self, data):
        data = u'' if data is None else data
        portal_transforms = self.tools['portal_transforms']
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        data = portal_transforms.convert('markdown_to_html', data)
        result = data.getData()
        if isinstance(result, str):
            result = result.decode('utf-8')
        return result

    def current_saved_by(self):
        if self.data and 'saved_by' in self.data:
            data = { 'id': self.data['saved_by'] }
            self.augment_user_data(data)
            return data
        return None

    def compass_url(self):
        return self.context.absolute_url() + '/@@compass'

    def base_url(self):
        return self.context.absolute_url() + '/@@compass/history/'

    def delete_url(self):
        return self.base_url() + str(self.key) + '/delete'

    def list_keys_url(self):
        return self.base_url() + str(self.key) + '/list_keys'

    def active_date(self):
        if self.data and 'plan_start' in self.data:
            active_date = self.data['plan_start']
        else:
            active_date = DateTime(self.key)
        return api.date.format(active_date)

    @api.jsonutils.jsonmethod()
    def do_list_keys(self):
        start = int(self.request.form.get('start', '0'), 10)
        portal_compass = self.tools['portal_compass']
        items = []
        for tstamp in portal_compass.keys(start, self.STEP):
            items.append({
                'value': tstamp,
                'url': self.base_url() + str(tstamp)
            })
        return {
            'items': items,
            'count': len(portal_compass)
        }

    def can_edit(self):
        return checkPermission('simplemanagement.EditCompass', self.context)

    @api.permissions.accesscontrol('simplemanagement.EditCompass')
    def do_delete(self):
        key = self.request.form.get('key')
        confirmation = self.request.form.get('do_delete')
        if key and confirmation and long(key) == self.key \
                and confirmation == 'yes':
            portal_compass = self.tools['portal_compass']
            portal_compass.remove(self.key)
            max_key = portal_compass.max_key()
            if max_key is not None:
                self.request.response.redirect(self.base_url() + str(max_key))
            else:
                self.request.response.redirect(self.compass_url())
            plone.api.portal.show_message(
                message=_(u"Snapshot deleted"),
                request=self.request
            )
        else:
            self.request.response.redirect(self.base_url() + str(self.key))
            plone.api.portal.show_message(
                message=_(u"Deletion has been cancelled"),
                request=self.request
            )

    def publishTraverse(self, request, name):
        if self.data is None:
            portal_compass = self.tools['portal_compass']
            key = long(name, 10)
            if key in portal_compass:
                self.key = key
                self.data = portal_compass[key]
                return self
        return super(History, self).publishTraverse(request, name)

    def __call__(self):
        if self.data is None:
            portal_compass = self.tools['portal_compass']
            max_key = portal_compass.max_key()
            if max_key is not None:
                self.request.response.redirect(self.base_url() + str(max_key))
                return u''

        return super(History, self).__call__()


class Compass(api.views.Traversable, CompassMixIn):

    STEP = 20  # Used for pagination/infinite scroll

    def __init__(self, context, request):
        super(Compass, self).__init__(context, request)
        self.tools = api.portal.LazyTools(context)

    def translations(self):
        data = {
            "week": _(u"{week} week"),
            "weeks": _(u"{week} weeks"),
            "person-added": _(u"{person} has been added to {project}"),
            "person-removed": _(u"{person} has been removed from {project}"),
            "error-please-reload": _(
                u'An error has occurred, '
                u'please <a href="{url}">reload the page clicking here</a>'
            ),
            "new-role": _(u"{name} is now a {role} in {project}"),
            "new-effort": _(u"{name} should put {effort} man days"
                            u" in {project}"),
            "new-project-effort": _(
                u"{project} will now require {effort} man days"
            ),
            "changes-saved": _(u"Changes saved"),
            "priority-updated": _(u"Priority updated"),
            "invalid-required": _(u"This field is required"),
            "invalid-number-value": _(
                u"You should insert a number here: e.g. 10.0"
            ),
            "project-activated": _(u"{project} has been activated"),
            "project-deactivated": _(u"{project} has been deactivated"),
            "project-created": _(u"{project} has been created"),
            "snapshot-taken": _(u"The situation has been saved"),
            "project-invalid": _(u"{project} is not valid"),
            "double-click-select": _(u"(double click to select)"),
            "double-click-unselect": _(u"(double click to reset selection)")
        }
        return json.dumps({
            k: self.context.translate(v) for k, v in data.items()
        })

    def global_settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ISettings)

    def working_week_days(self):
        global_settings = self.global_settings()
        return global_settings.working_week_days

    def warning_delta(self):
        global_settings = self.global_settings()
        return global_settings.warning_delta_percent

    def settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ICompassSettings)

    def roles(self):
        roles_factory = getUtility(
            IVocabularyFactory,
            name="collective.simplemanagement.roles"
        )
        roles = {}
        for term in roles_factory(self.context):
            roles[term.token] = {
                'name': term.title,
                'shortname': api.text.shorten(term.title, 3)
            }
        return json.dumps(roles)

    def employees(self):
        users = {}
        for user_id in api.users.get_employee_ids(self.context):
            user_details = api.users.get_user_details(
                self.context,
                user_id,
                portal_url=self.tools['portal_url'],
                portal_membership=self.tools['portal_membership']
            )
            users[user_id] = {
                'name': user_details['fullname'],
                'avatar': user_details['portrait']
            }
        return json.dumps(users)

    def base_url(self):
        return self.context.absolute_url() + '/@@compass/'

    def last_snapshot(self):
        last = self.tools['portal_compass'].max_key()
        if last is not None:
            return '{0}history/{1}'.format(self.base_url(), last)
        return ''

    def _get_project_info(self, project, brain=None):
        info = {}
        if brain is not None:
            info.update({
                'id': brain.getPath(),
                'uid': brain.UID,
                'url': brain.getURL(),
                'name': brain.Title,
                'status': brain.review_state,
                'customer': brain.customer,
                'priority': brain.priority
            })
        else:
            pw = self.tools['portal_workflow']
            status = pw.getStatusOf("project_workflow", project)
            info.update({
                'id': '/'.join(project.getPhysicalPath()),
                'name': project.title_or_id(),
                'status': status['review_state'],
                'customer': project.customer,
                'priority': project.priority
            })
        info.update({
            'people': self._get_operatives(project),
            'effort': str(project.compass_effort),
            'notes': project.compass_notes,
            'active': project.active
        })
        return info

    @staticmethod
    def _get_operatives(project):
        people = []
        if project.operatives is not None:
            for operative in project.operatives:
                if operative.active:
                    people.append({
                        'id': operative.user_id,
                        'role': operative.role,
                        'effort': str(operative.compass_effort)
                    })
        return people

    @staticmethod
    def _add_operative(user_id, role, effort, operatives):
        for operative in operatives:
            if operative.user_id == user_id:
                operative.role = role
                operative.compass_effort = effort
                operative.active = True
                return False
        operative = Resource()
        operative.role = role
        operative.user_id = user_id
        operative.active = True
        operative.compass_effort = effort
        operatives.append(operative)
        return True

    @staticmethod
    def _del_operative(user_id, operatives):
        for operative in operatives:
            if operative.user_id == user_id:
                operative.active = False
                operative.compass_effort = Decimal('0.00')
                return True
        return False

    def _get_project_by_id(self, project_id, portal=None):
        if portal is None:
            portal = self.tools['portal_url'].getPortalObject()
        return portal.restrictedTraverse(project_id)

    @api.jsonutils.jsonmethod()
    def do_set_project_data(self):
        project = self._get_project_by_id(self.request.form['project'])
        data = json.loads(self.request.form['data'])
        if 'active' in data:
            project.active = data['active']
        if 'priority' in data:
            project.priority = data['priority']
        if 'notes' in data:
            project.compass_notes = data['notes']
        if 'effort' in data:
            project.compass_effort = Decimal(data['effort'])
        if 'people' in data:
            operatives = project.operatives
            if operatives is None:
                operatives = []
            for person in data['people']:
                if person.get('remove', False):
                    self._del_operative(person['id'], operatives)
                else:
                    self._add_operative(
                        person['id'],
                        person['role'],
                        Decimal(person['effort']),
                        operatives
                    )
            if len(operatives) > 0:
                project.operatives = operatives
        # TODO: reindex only necessary index
        project.reindexObject()
        return self._get_project_info(project)

    @api.jsonutils.jsonmethod()
    def do_set_priority(self):
        pu = self.tools['portal_url']
        portal = pu.getPortalObject()
        projects = self.request.form['projects_ids']
        return_value = {}
        for index, project_id in enumerate(projects):
            project = self._get_project_by_id(project_id, portal=portal)
            project.priority = index + 1
            project.reindexObject('priority')
            return_value[project_id] = project.priority
        return return_value

    @api.jsonutils.jsonmethod()
    def do_get_projects(self):
        projects = []
        pc = self.tools['portal_catalog']
        for brain in pc.searchResults(portal_type='Project',
                                      active=True,
                                      sort_on='priority'):
            project = brain.getObject()
            projects.append(self._get_project_info(project, brain))
        return projects

    @api.jsonutils.jsonmethod()
    def do_get_all_projects(self):
        start = int(self.request.form.get('start', '0'), 10)
        query = self.request.form.get('query')
        pc = self.tools['portal_catalog']
        kwargs = {
            'portal_type': 'Project',
            'active': False,
            'sort_on': 'priority'
        }
        if query:
            # TODO: I tried to use searchabletext
            # but we don't seem to index well there
            kwargs['Title'] = query
        brains = pc.searchResults(**kwargs)
        total_count = len(brains)
        brains = brains[start:start+self.STEP]
        projects = []
        for brain in brains:
            project = brain.getObject()
            projects.append(self._get_project_info(project, brain))
        return {
            'items': projects,
            'count': total_count
        }

    @api.jsonutils.jsonmethod()
    def do_create_project(self):
        settings = self.settings()
        projects_folder = plone.api.content.get(
            path=settings.projects_folder.encode('utf-8')
        )
        if projects_folder is None:
            projects_folder = plone.api.portal.get()
        data = json.loads(self.request.form['data'])
        priority = int(self.request.form['priority'], 10)
        initial_estimate = None
        if 'estimate' in data:
            initial_estimate = Decimal(data['estimate'])
        project = plone.api.content.create(
            container=projects_folder,
            type='Project',
            title=data['name'],
            customer=data['customer'],
            budget=Decimal(data['budget']),
            initial_estimate=initial_estimate,
            prj_start_date=date.today()
        )
        project.priority = priority
        project.reindexObject()
        return self._get_project_info(project)

    @api.jsonutils.jsonmethod()
    def do_take_snapshot(self):
        data = json.loads(self.request.form['data'])
        current_user = plone.api.user.get_current()
        data['saved_by'] = current_user.id
        portal_compass = self.tools['portal_compass']

        # Convert date
        data['plan_start'] = datetime.strptime(
            data['plan_start'], '%Y-%m-%d').date()
        data['plan_end'] = datetime.strptime(
            data['plan_end'], '%Y-%m-%d').date()

        key = portal_compass.add(data)
        return {
            'url': '{0}history/{1}'.format(
                self.base_url(),
                key
            )
        }

    def publishTraverse(self, request, name):
        if self.method is None and name == 'history':
            return History(self.context, self.request)
        return super(Compass, self).publishTraverse(request, name)

    def __call__(self):
        if checkPermission('simplemanagement.EditCompass', self.context):
            return super(Compass, self).__call__()
        elif checkPermission('simplemanagement.ViewCompass', self.context):
            self.request.response.redirect('{0}history'.format(self.base_url()))
            return u''
        raise Unauthorized
