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


class Compass(BrowserView):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(Compass, self).__init__(context, request)
        self.method = None

    def roles(self):
        roles_factory = getUtility(
            IVocabularyFactory,
            name="collective.simplemanagement.roles"
        )
        roles = {}
        for term in roles_factory(self.context):
            roles[term.token] = {
                'name': term.title,
                'shortname': shorten(term.title, 4)
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
        base = self.context.absolute_url()
        return json.dumps({
            'projects': {
                'get': base + '/@@compass/get_projects'
            },
            'project': {
                'get': base + '/@@compass/get_project_info'
            }
        })

    @staticmethod
    def _get_operatives(project):
        people = {}
        if project.operatives is not None:
            for operative in project.operatives:
                if operative.active:
                    people.setdefault(operative.role, []).append(
                        operative.user_id
                    )
        return people

    @jsonmethod()
    def do_get_project_info(self):
        pc = getToolByName(self.context, 'portal_catalog')
        pu = getToolByName(self.context, 'portal_url')
        project = pu.getPortalObject().restrictedTraverse(
            self.request.form['id']
        )
        project_info = {
            'people': self._get_operatives(project),
            'iterations': []
        }
        now = DateTime()
        query = {
            'path': '/'.join(project.getPhysicalPath()),
            'portal_type': 'Iteration',
            'end': {
                'query': now-1,
                'range': 'min'
            },
            'sort_on': 'end'
        }
        iterations = pc.searchResults(query)
        for iteration in iterations:
            project_info['iterations'].append({
                'effort': int(iteration.estimate),
                'start': iteration.start,
                'end': iteration.end
            })
        if len(project_info['iterations']) > 0:
            project_info['end'] = project_info['iterations'][0]['end']
        return project_info

    @jsonmethod()
    def do_get_projects(self):
        projects = []
        pc = getToolByName(self.context, 'portal_catalog')
        for brain in pc.searchResults(portal_type='Project',
                                      sort_on='priority'):
            info = {
                'id': brain.getPath(),
                'name': brain.Title,
                'status': brain.review_state,
                'active': brain.active,
                'customer': brain.customer,
                'priority': brain.priority
            }
            if brain.active:
                project = brain.getObject()
                info['people'] = self._get_operatives(project)
                now = DateTime()
                query = {
                    'path': '/'.join(project.getPhysicalPath()),
                    'portal_type': 'Iteration',
                    'start': {
                        'query': now+1,
                        'range': 'max'
                    },
                    'end': {
                        'query': now-1,
                        'range': 'min'
                    },
                    'sort_on': 'end'
                }
                iterations = pc.searchResults(query)
                if len(iterations) == 0:
                    del query['end']
                    query['start']['range'] = 'min'
                    iterations = pc.searchResults(query)[:1]
                total_days = reduce(
                    lambda x, y: x + y.estimate,
                    iterations,
                    Decimal('0.00')
                )
                if len(iterations) > 0:
                    info['effort'] = int(total_days)
                    info['end'] = iterations[-1].end
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
