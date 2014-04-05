from Acquisition import aq_parent

from z3c.relationfield.relation import RelationValue

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.dexterity.utils import createContentInContainer

from ..interfaces import IStory
from ..interfaces import IIteration
from ..interfaces import IProject


def create_story(context, data, reindex=True):
    ## XXX FIXME 2013-06-15:
    ## subjects are stored into 'subject' attribute
    ## see https://github.com/plone/plone.app.dexterity/blob/master/plone/app/dexterity/behaviors/metadata.py#L331
    ## we should use behavior magic to do this
    if 'subjects' in data:
        data['subject'] = data.pop('subjects')
    # make sure we don't get duplicates for assignees
    data['assigned_to'] = list(set(data['assigned_to'] or []))
    item = createContentInContainer(
        context,
        'Story',
        **data
    )
    if reindex:
        item.reindexObject()
    return item


def get_ancestor(iface, context, default=None):
    """Gets the ancestor of ``context`` providing ``iface``.

    Returns ``default`` if not found.
    """
    current = context
    while current is not None:
        if iface.providedBy(current):
            return current
        # stop when Plone site is found
        if IPloneSiteRoot.providedBy(current):
            return default
        current = aq_parent(current)
    return default


def get_story(context, default=None):
    return get_ancestor(IStory, context, default)


def get_project(context, default=None):
    return get_ancestor(IProject, context, default)


def get_iteration(context, default=None):
    return get_ancestor(IIteration, context, default)


def get_epic_by_story(story):
    obj = getattr(story, 'epic', None)
    if not obj:
        return {}

    if isinstance(obj, RelationValue):
        if obj.isBroken():
            return

        obj = obj.to_object

    if not obj:
        return {}

    return {
        'url': obj.absolute_url(),
        'title': obj.title
    }


def get_wf_state_info(brain, context=None):
    """Returns some informations on workflow state

    :param obj: Object
    :returns: name and title of workflow state
    :rtype: dict
    """
    if not context:
        purl = getToolByName(brain, 'portal_url')
        context = purl.getPortalObject()
    wt = getToolByName(context, 'portal_workflow')
    _info = {
        'title': None,
        'state': None
    }

    _info['state'] = brain.review_state
    # wt.getInfoFor(obj, 'review_state')
    if _info['state']:
        _info['title'] = context.translate(
            wt.getTitleForStateOnType(
                _info['state'], brain.portal_type
            )
        )

    return _info


class BreadcrumbGetter(object):
    """Gets a breadcrumb from a brain
    """

    def __init__(self, catalog):
        self.catalog = catalog

    def get_title(self, path):
        results = self.catalog.searchResults(path={
            'query': path,
            'depth': 0
        })
        if len(results) > 0:
            return results[0]['Title']
        return None

    def __call__(self, brain):
        breadcrumb = []
        path = brain.getPath()
        breadcrumb.append(self.get_title(path))
        path_components = path.split("/")
        for i in xrange(1, len(path_components)):
            title = self.get_title("/".join(path_components[:-1*i]))
            if title is not None:
                breadcrumb.append(title)
        breadcrumb.reverse()
        return breadcrumb
