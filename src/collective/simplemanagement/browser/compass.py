import json
import plone.api
from datetime import date
from decimal import Decimal
from zope.interface import implements
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.registry.interfaces import IRegistry
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from ..interfaces.settings import ISettings
from ..interfaces.compass import ICompassSettings
from .. import api
from ..structures import Resource
from .. import messageFactory as _

# Validate both on the server and client side,
# using z3c.form on the client side in a less stressful way

class Compass(BrowserView):

    implements(IPublishTraverse)

    STEP = 20 # Used for pagination/infinite scroll

    def __init__(self, context, request):
        super(Compass, self).__init__(context, request)
        self.method = None

    def translations(self):
        return json.dumps({
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
            "project-created": _(u"{project} has been created")
        })

    def global_settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ISettings)

    def working_week_days(self):
        global_settings = self.global_settings()
        return global_settings.working_week_days

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
        pu = getToolByName(self.context, 'portal_url')
        pm = getToolByName(self.context, 'portal_membership')
        users = {}
        for user_id in api.users.get_employee_ids(self.context):
            user_details = api.users.get_user_details(
                self.context,
                user_id,
                portal_url=pu,
                portal_membership=pm
            )
            users[user_id] = {
                'name': user_details['fullname'],
                'avatar': user_details['portrait']
            }
        return json.dumps(users)

    def base_url(self):
        return self.context.absolute_url() + '/@@compass/'

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
            pu = getToolByName(self.context, 'portal_url')
            portal = pu.getPortalObject()
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

    def _get_project_info(self, project, brain=None):
        info = {}
        if brain is not None:
            info.update({
                'id': brain.getPath(),
                'name': brain.Title,
                'status': brain.review_state,
                'customer': brain.customer,
                'priority': brain.priority
            })
        else:
            pw = getToolByName(self.context, "portal_workflow")
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

    @api.jsonutils.jsonmethod()
    def do_set_priority(self):
        pu = getToolByName(self.context, 'portal_url')
        portal = pu.getPortalObject()
        projects = self.request.form['projects_ids']
        return_value = {}
        for index, project_id in enumerate(projects):
            project = self._get_project_by_id(project_id, portal=portal)
            project.priority = index + 1
            project.reindexObject('priority')
            return_value[project_id] = project.priority
        return return_value

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

    @api.jsonutils.jsonmethod()
    def do_get_projects(self):
        projects = []
        pc = getToolByName(self.context, 'portal_catalog')
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
        pc = getToolByName(self.context, 'portal_catalog')
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

    def publishTraverse(self, request, name):
        if self.method is None:
            method = getattr(self, 'do_'+name, None)
            if method is not None and callable(method):
                self.method = 'do_'+name
            return self
        raise NotFound(self, name, request)

    def __call__(self):
        if self.method is None:
            result = super(Compass, self).__call__()
        else:
            result = getattr(self, self.method)()
        self.method = None
        return result
