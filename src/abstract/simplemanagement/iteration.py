from five import grok
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName

from .interfaces import IIteration
from .utils import get_timings
from .utils import get_user_details


class View(grok.View):
    grok.context(IIteration)
    grok.require('zope2.View')

    WARNING_DELTA = 3

    @memoize
    def stories(self):
        stories = []
        pc = getToolByName(self.context, 'portal_catalog')
        stories_brains = pc.searchResults({
            'path': '/'.join(self.context.getPhysicalPath()),
            'portal_type': 'Story',
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'
        })
        for brain in stories_brains:
            story = brain.getObject()
            timings = get_timings(story, portal_catalog=pc)
            epic = None
            if story.epic and not story.epic.isBroken():
                epic = {
                    'url': story.epic.to_object.absolute_url(),
                    'title': story.epic.to_object.title
                }

            def _get_assignees(context, assignees):
                for user_id in assignees:
                    yield get_user_details(context, user_id)

            stories.append({
                'status': brain.review_state,
                'url': brain.getURL,
                'description': brain.Description,
                'title': brain.Title,
                'estimate': timings['estimate'],
                'hours': timings['resource_time'],
                'difference': timings['difference'],
                'time_status': timings['status'],
                'epic': epic,
                'assignees': _get_assignees(self.context, story.assigned_to)
            })
        return stories
