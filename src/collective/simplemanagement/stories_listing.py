from zope.interface import implements

from plone.app.discussion.interfaces import IConversation

from Products.CMFCore.utils import getToolByName

from .interfaces import IStoriesListing
from .utils import get_timings
from .utils import get_assignees_details
from .utils import get_epic_by_story
from .utils import get_timing_status


class StoriesListing(object):
    implements(IStoriesListing)

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

    def _stories(self):
        pc = self.portal_catalog
        stories_brains = pc.searchResults({
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1
            },
            'portal_type': 'Story',
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'
        })
        return stories_brains

    def comments(self, story):
        conversation = IConversation(story)
        return [i for i in conversation.getThreads()]

    def stories(self):
        brains = self._stories()
        stories = []
        self.totals = {
            'hours': 0,
            'difference': 0,
            'estimate': 0
        }

        for brain in brains:
            story = brain.getObject()
            timings = get_timings(story, portal_catalog=self.portal_catalog)

            self.totals['estimate'] += timings['estimate']
            self.totals['hours'] += timings['resource_time']
            self.totals['difference'] += timings['difference']

            stories.append({
                'id': brain.getId,
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
                'comments': self.comments(story),
                'can_edit': story.user_can_edit(),
                'can_review': story.user_can_review()
            })

        self.totals['time_status'] = get_timing_status(
            self.totals['difference']
        )
        return stories
