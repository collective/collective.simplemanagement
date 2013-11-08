from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

from ...interfaces import IEpic, IStory
from ...configure import Settings
from ... import api


class View(BrowserView):

    @memoize
    def contained(self, depth=1, with_object=False):
        contained = []
        pc = getToolByName(self.context, 'portal_catalog')
        context_path = '/'.join(self.context.getPhysicalPath())
        query = {
            'portal_type': 'Epic'
        }
        if depth is None:
            query['path'] = context_path
        else:
            query['path'] = {
                'query': context_path,
                'depth': depth
            }
        contained_epics = pc.searchResults(query)
        for epic in contained_epics:
            if epic.getPath() != context_path:
                if with_object:
                    contained.append(epic.getObject())
                else:
                    contained.append({
                        'title': epic.Title,
                        'description': epic.Description,
                        'url': epic.getURL(),
                        'estimate': epic.estimate
                    })
        return contained

    @memoize
    def stories(self, all=False):
        stories = []
        intids = getUtility(IIntIds)
        catalog = getUtility(ICatalog)
        contexts = [self.context]
        if all:
            contexts.extend(self.contained(depth=None, with_object=True))
        for context in contexts:
            relations = catalog.findRelations({
                'to_id': intids.getId(context),
                'from_interfaces_flattened': IStory
            })
            for rel in relations:
                stories.append(rel.from_object)
        return stories

    def timings(self):
        settings = Settings()
        stories_estimate = 0
        time_spent = 0
        for story in self.stories(all=True):
            timings = api.booking.get_timings(story)
            stories_estimate += timings['estimate']
            time_spent += timings['resource_time']
        contained = self.contained()
        estimates = {
            'epic': self.context.estimate * settings.man_day_hours,
            'stories': stories_estimate,
            'contained': False
        }
        differences = {
            'stories':  estimates['stories'] - estimates['epic'],
            'spent': time_spent - estimates['epic'],
            'contained': False
        }
        classes = {
            'stories':  api.booking.get_difference_class(
                estimates['epic'],
                estimates['stories'],
                settings),
            'spent': api.booking.get_difference_class(
                estimates['epic'],
                time_spent,
                settings),
            'contained': False
        }
        if len(contained) > 0:
            estimates['contained'] = sum(
                [c['estimate'] for c in contained]) * settings.man_day_hours
            differences['contained'] = estimates['contained'] - \
                estimates['epic']
            classes['contained'] = api.booking.get_difference_class(
                estimates['epic'],
                estimates['contained'],
                settings
            )
        return {
            'estimates': estimates,
            'time_spent': time_spent,
            'differences': differences,
            'classes': classes
        }
