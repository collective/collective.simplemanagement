from zope.interface import implementer
from plone.dexterity.content import Container

from . import api
from .configure import Settings
from .interfaces import IIteration
from .interfaces import IStoriesListing
from .utils import quantize
from .timeline import BaseTimeline
from .timeline import timeline


@implementer(IIteration)
class Iteration(Container):
    """Iteration content type"""

    def _stories_listing(self):
        return IStoriesListing(self)()

    def stories(self):
        return self._stories_listing().stories

    def totals(self):
        return self._stories_listing().totals


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
            timings = api.booking.get_timings(context)
            if 'todo' in indexes:
                values['todo'] = timings['estimate']
            if 'done' in indexes:
                values['done'] = timings['resource_time']
        return values
