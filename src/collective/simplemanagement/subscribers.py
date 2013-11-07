# pylint: disable=W0613
from zope.lifecycleevent.interfaces import IObjectMovedEvent

from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName

from .interfaces import IIteration
from .timeline import snapshot
from .utils import get_iteration
from .configure import TRACKER_ID, DOCUMENTS_ID
from . import messageFactory as _


def create_project_collaterals(obj, event):
    """Creates a PoiTracker and a Documents folder within a new project
    """
    _translate = lambda c, v: c.translate(v)
    _title = obj.title or u'Project'
    if TRACKER_ID not in obj:
        obj.invokeFactory('PoiTracker', TRACKER_ID)
        tracker = obj[TRACKER_ID]
        title = _(
            u"${project_name}'s issues",
            mapping={'project_name': _title}
        )
        description = _(
            u"The issues relative to ${project_name}",
            mapping={'project_name': _title}
        )
        helper_text = _(
            u"<p>Here are collected all the issues "
            u"relative to the project <em>${project_name}</em>.</p>"
            u"<p>If you found any problems, "
            u"please report it here by clicking "
            u"<em>New issue</em>.</p>", mapping={'project_name': _title}
        )

        tracker.setTitle(_translate(obj, title))
        tracker.setDescription(_translate(obj, description))
        tracker.setHelpText(_translate(obj, helper_text))
        if obj.operatives:
            tracker.setManagers([o.user_id for o in obj.operatives])

        workflowTool = getToolByName(tracker, "portal_workflow")
        try:
            workflowTool.doActionFor(tracker, "protect")
        except WorkflowException:
            pass

        tracker.reindexObject()
    if DOCUMENTS_ID not in obj:
        obj.invokeFactory('Folder', DOCUMENTS_ID)
        documents = obj[DOCUMENTS_ID]
        title = _(
            u"${project_name}'s documents",
            mapping={'project_name': _title}
        )
        description = _(
            u"The documents that have been gathered "
            u"for ${project_name}", mapping={'project_name': _title}
        )
        documents.setTitle(_translate(obj, title))
        documents.setDescription(_translate(obj, description))
        documents.reindexObject()


def update_tracker_managers(obj, event):
    """If operatives have been added to the project,
    adds them as the default tracker managers too.
    """
    if TRACKER_ID not in obj:
        create_project_collaterals(obj, event)
    else:
        tracker = obj[TRACKER_ID]
        tracker_managers = list(tracker.getManagers())
        changed = False
        operatives = obj.operatives or []
        for operative in operatives:
            if operative.user_id not in tracker_managers:
                tracker_managers.append(operative.user_id)
                changed = True
        if changed:
            tracker.setManagers(tracker_managers)
            tracker.reindexObject()


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
