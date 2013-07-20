from zope.interface import implements

from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from plone.app.discussion.interfaces import IConversation

from Products.CMFCore.utils import getToolByName

from .interfaces import IStoriesListing
from .interfaces import IUserStoriesListing
from .utils import get_timings
from .utils import get_assignees_details
from .utils import get_epic_by_story
from .utils import get_difference_class
from .utils import get_iteration
from .utils import get_project


class StoriesListing(object):
    implements(IStoriesListing)
    _user_id = None
    totals = {
        'hours': 0,
        'difference': 0,
        'estimate': 0
    }

    def __init__(self, context):
        self.context = context

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @memoize
    def portal_state(self):
        return self.context.restrictedTraverse('plone_portal_state')

    @property
    def user_id(self):
        user_id = self._user_id
        portal_state = self.portal_state()
        if not (user_id or portal_state.anonymous()):
            user_id = portal_state.member().getId()
        return user_id

    @property
    def _query(self):
        return {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1
            },
            'portal_type': 'Story',
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'
        }

    def _stories(self, story_states=None):
        pc = self.portal_catalog
        query = self._query
        if story_states:
            query['review_state'] = story_states
        stories_brains = pc.searchResults(query)
        return stories_brains

    # def comments(self, story):
    #     conversation = IConversation(story)
    #     return [i for i in conversation.getThreads()]

    def stories(self, project_states=None, story_states=None, 
                project_info=False):
        brains = self._stories(story_states)
        pw = getToolByName(self.context, 'portal_workflow')
        stories = []
        self.totals = {
            'hours': 0,
            'difference': 0,
            'estimate': 0
        }

        for brain in brains:
            story = brain.getObject()
            project = get_project(story)
            if project_states:
                _state = pw.getInfoFor(project, 'review_state')
                if _state not in project_states:
                    continue

            timings = get_timings(story, portal_catalog=self.portal_catalog)

            self.totals['estimate'] += timings['estimate']
            self.totals['hours'] += timings['resource_time']
            self.totals['difference'] += timings['difference']

            data = {
                'id': brain.getId,
                'UID': IUUID(story),
                'text': story.get_text(),
                'status': brain.review_state,
                'url': brain.getURL(),
                'description': brain.Description,
                'title': brain.Title,
                'estimate': timings['estimate'],
                'resource_time': timings['resource_time'],
                'difference': timings['difference'],
                'time_status': timings['time_status'],
                'epic': get_epic_by_story(story),
                'assignees': get_assignees_details(story),
                'can_edit': story.user_can_edit(),
                'can_review': story.user_can_review(),
                'milestone': story.get_milestone()
            }

            if project_info:
                iteration = get_iteration(story)
                data.update({
                    'project': {
                        'title': project.Title(),
                        'description': project.Description(),
                        'url': project.absolute_url(),
                        'priority': project.priority,
                        'UID': IUUID(project),
                    },
                })
                if iteration:
                    data.update({
                        'iteration': {
                            'title': iteration.Title(),
                            'description': iteration.Description(),
                            'url': iteration.absolute_url(),
                            'UID': IUUID(iteration)
                        }
                    })
            stories.append(data)

        self.totals['time_status'] = get_difference_class(
            self.totals['estimate'],
            self.totals['hours']
        )
        return stories


class UserStoriesListing(StoriesListing):
    implements(IUserStoriesListing)

    @property
    def _query(self):
        return {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
            },
            'portal_type': 'Story',
            'assigned_to': self.user_id,
            'review_state': ('todo', 'suspended', 'in_progress')
        }

    def stories(self, project_states=None, story_states=None,
                project_info=False, user_id=None):
        self._user_id = user_id
        stories = super(UserStoriesListing, self).stories(
            project_states=project_states,
            story_states=story_states,
            project_info=project_info
        )
        return stories
