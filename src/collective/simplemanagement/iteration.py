from five import grok

from zope.interface import implementer
from plone.dexterity.content import Container

from .configure import Settings
from .interfaces import IIteration
from .utils import quantize
from .utils import get_timings
from .timeline import BaseTimeline
from .timeline import timeline


@implementer(IIteration)
class Iteration(Container):
    """Iteration content type"""


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
