import json
from decimal import Decimal
from zope.interface import implements
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces import IPublishTraverse, NotFound
from plone.registry.interfaces import IRegistry
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
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
            "invalid-number-value": _(
                u"You should insert a number here: e.g. 10.0"
            )
        })

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
            'notes': project.compass_notes
        })
        return info

    @api.jsonutils.jsonmethod()
    def do_deactivate_project(self):
        project = self._get_project_by_id(self.request.form['project'])
        project.active = False
        project.reindexObject('active')
        return { 'id': '/'.join(project.getPhysicalPath()), 'active': False }

    @api.jsonutils.jsonmethod()
    def do_set_priority(self):
        pu = getToolByName(self.context, 'portal_url')
        portal = pu.getPortalObject()
        projects = self.request.form['projects_ids']
        return_value = []
        for index, project_id in enumerate(projects):
            project = self._get_project_by_id(project_id, portal=portal)
            project.priority = index + 1
            project.reindexObject('priority')
            return_value.append({ 'id': project_id, 'priority': index + 1 })
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
        start = int(self.request.form.get('projects_ids', '0'), 10)
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc.searchResults(portal_type='Project',
                                  sort_on='priority')
        brains = brains[start:self.STEP]
        projects = []
        for brain in brains:
            project = brain.getObject()
            projects.append(self._get_project_info(project, brain))
        return projects

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
