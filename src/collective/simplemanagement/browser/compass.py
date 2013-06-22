import json
from decimal import Decimal
from DateTime import DateTime
from zope.interface import implements
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces import IPublishTraverse, NotFound
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from ..utils import get_employee_ids, get_user_details, jsonmethod, shorten
from .. import messageFactory as _


class Compass(BrowserView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(Compass, self).__init__(context, request)
        self.method = None

    def translations(self):
        return json.dumps({
            "week": _("week"),
            "weeks": _("{week} weeks"),
            "day": _("{day} day"),
            "days": _("{day} days"),
            "no_effort": _(u"No effort planned"),
            "effort": _(u"{days} in the next {weeks}")
        })

    def roles(self):
        roles_factory = getUtility(
            IVocabularyFactory,
            name="collective.simplemanagement.roles"
        )
        roles = {}
        for term in roles_factory(self.context):
            roles[term.token] = {
                'name': term.title,
                'shortname': shorten(term.title, 3)
            }
        return json.dumps(roles)

    def employees(self):
        pu = getToolByName(self.context, 'portal_url')
        pm = getToolByName(self.context, 'portal_membership')
        users = {}
        for user_id in get_employee_ids(self.context):
            user_details = get_user_details(
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

    def urls(self):
        base = self.context.absolute_url() + '/@@compass/'
        urls = {}
        for method_ in ['set_project_data', 'get_projects',
                        'get_all_projects']:
            urls[method_] = base + method_
        return json.dumps(urls)

    @jsonmethod()
    def do_get_all_projects(self):
        pass

    @jsonmethod()
    def do_set_project_data(self):
        pu = getToolByName(self.context, 'portal_url')
        portal = pu.getPortalObject()
        project = portal.restrictedTraverse(self.request.form['project'])
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
                    pass
                else:
                    pass

    @jsonmethod()
    def do_swap_priority(self):
        pass

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

    @jsonmethod()
    def do_get_projects(self):
        projects = []
        pc = getToolByName(self.context, 'portal_catalog')
        for brain in pc.searchResults(portal_type='Project',
                                      active=True,
                                      sort_on='priority'):
            project = brain.getObject()
            info = {
                'id': brain.getPath(),
                'name': brain.Title,
                'status': brain.review_state,
                'customer': brain.customer,
                'priority': brain.priority,
                'people': self._get_operatives(project),
                'effort': str(project.compass_effort),
                'notes': project.compass_notes
            }
            projects.append(info)
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
