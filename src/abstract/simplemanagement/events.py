# pylint: disable=W0613
from . import messageFactory as _
from .configure import TRACKER_ID, DOCUMENTS_ID


def create_project_collaterals(obj, event):
    """Creates a PoiTracker and a Documents folder within a new project
    """
    _title = obj.title or u'Project'
    if TRACKER_ID not in obj:
        obj.invokeFactory('PoiTracker', TRACKER_ID)
        tracker = obj[TRACKER_ID]
        tracker.setTitle(
            _(u"%(project_name)s's issues") % {
                'project_name': _title
            }
        )
        tracker.setDescription(
            _(u"The issues relative to %(project_name)s") % {
                'project_name': _title
            }
        )
        tracker.setHelpText(
            _(u"<p>Here are collected all the issues "
              u"relative to the project <em>%(project_name)s</em>.</p>"
              u"<p>If you found any problems, "
              u"please report it here by clicking <em>New issue</em>.</p>") % {
                'project_name': _title
            }
        )
        if obj.operatives:
            tracker.setManagers([ o.user_id for o in obj.operatives ])
        tracker.reindexObject()
    if DOCUMENTS_ID not in obj:
        obj.invokeFactory('Folder', DOCUMENTS_ID)
        documents = obj[DOCUMENTS_ID]
        documents.setTitle(
            _(u"%(project_name)s's documents") % {
                'project_name': _title
            }
        )
        documents.setDescription(
            _(u"The documents that have been gathered for %(project_name)s") % {
                'project_name': _title
            }
        )
        documents.reindexObject()


def update_tracker_managers(obj, event):
    """If operatives have been added to the project,
    adds them as the default tracker managers too.
    """
    if TRACKER_ID not in obj:
        create_project_collaterals(obj, event)
    else:
        tracker = obj[TRACKER_ID]
        tracker_managers = tracker.getManagers()
        changed = False
        operatives = obj.operatives or []
        for operative in operatives:
            if operative.user_id not in tracker_managers:
                tracker_managers.append(operative.user_id)
                changed = True
        if changed:
            tracker.setManagers(tracker_managers)
            tracker.reindexObject()
