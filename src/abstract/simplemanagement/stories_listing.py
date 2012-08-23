from zope.interface import implements

from plone.app.discussion.interfaces import IConversation

from Products.CMFCore.utils import getToolByName

from .interfaces import IStoriesListing
from .utils import get_timings
from .utils import get_assignees_details


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
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Story',
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'
        })
        return stories_brains

    def comments(self, story):
        conversation = IConversation(story)
        comments = [(i.author_name, i.text) for i in conversation.getComments()]
        return comments

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
            epic = None
            if story.epic and not story.epic.isBroken():
                epic = {
                    'url': story.epic.to_object.absolute_url(),
                    'title': story.epic.to_object.title
                }

            self.totals['estimate'] += timings['estimate']
            self.totals['hours'] += timings['resource_time']
            self.totals['difference'] += timings['difference']

            stories.append({
                'id': brain.getId,
                'text': story.text,
                'status': brain.review_state,
                'url': brain.getURL(),
                'description': brain.Description,
                'title': brain.Title,
                'estimate': timings['estimate'],
                'hours': timings['resource_time'],
                'difference': timings['difference'],
                'time_status': timings['status'],
                'epic': epic,
                'assignees': get_assignees_details(story),
                'comments': self.comments(story)
            })
        return stories
