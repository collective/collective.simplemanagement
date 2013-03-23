from Acquisition import aq_inner
from five import grok

from zope.security import checkPermission
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from z3c.form.interfaces import IFormLayer

from plone.memoize.instance import memoize
from plone.dexterity.content import Container

from plone.z3cform import z2

from .configure import Settings
from .interfaces import IIteration
from .interfaces import IStoriesListing
from .utils import quantize
from .utils import get_timings
from .utils import get_iteration
from .story import StoryQuickForm
from .timeline import BaseTimeline
from .timeline import timeline
from .timeline import snapshot


class Iteration(Container):
    grok.implements(IIteration)


# XXX: move somewhere else
class IterationViewMixin(object):

    totals = None

    @memoize
    def stories(self):
        adpt = IStoriesListing(self.context)
        stories = adpt.stories()
        self.totals = adpt.totals
        return stories

    @property
    def user_can_manage_project(self):
        return checkPermission(
            'simplemanagement.ManageProject', self.context
        )

    def user_can_edit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def user_can_add_story(self):
        return checkPermission('cmf.AddPortalContent', self.context)

    def add_story_form(self):
        z2.switch_on(self, request_layer=IFormLayer)
        addform = StoryQuickForm(aq_inner(self.context), self.request)
        addform.update()
        return addform.render()


class View(grok.View, IterationViewMixin):
    grok.context(IIteration)
    grok.require('zope2.View')

    def get_dates(self):
        start = self.context.toLocalizedTime(self.context.start.isoformat())
        end = self.context.toLocalizedTime(self.context.end.isoformat())
        return dict(start=start, end=end)


@timeline(IIteration)
class IterationTimeline(BaseTimeline):
    # pylint: disable=W0613

    indexes = (
        'estimate',
        'todo',
        'done'
    )

    def index(self, context, indexes, previous):
        settings = Settings()
        values = {}
        if 'estimate' in indexes:
            values['estimate'] = quantize(
                context.estimate * settings.man_day_hours
            )
        if 'todo' in indexes or 'done' in indexes:
            timings = get_timings(context)
            if 'todo' in indexes:
                values['todo'] = timings['estimate']
            if 'done' in indexes:
                values['done'] = timings['resource_time']
        return values


def timeline_update(object_, event):
    iterations = []
    if not IIteration.providedBy(object_):
        if IObjectMovedEvent.providedBy(event):
            for parent in [event.oldParent, event.newParent]:
                if parent:
                    iterations.append(get_iteration(parent))
        else:
            iterations.append(get_iteration(object_))
    else:
        iterations.append(object_)
    for iteration in iterations:
        if iteration is not None:
            snapshot(iteration)
