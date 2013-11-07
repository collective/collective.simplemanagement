from zope.lifecycleevent.interfaces import IObjectMovedEvent
from .interfaces import IIteration
from .timeline import snapshot
from .utils import get_iteration


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
