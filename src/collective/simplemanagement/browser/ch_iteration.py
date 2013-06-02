import json

from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.uuid.utils import uuidToObject
from ..utils import get_project


class ChangeIteration(BrowserView):

    ch_iteration_template = ViewPageTemplateFile('templates/ch_iteration.pt')

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def ch_iteration(self):
        """return a list of iterations available for the context
        """
        iterations = []
        iteration_context = aq_parent(aq_inner(self.context))
        project = get_project(self.context)
        query = {'path': {'query': '/'.join(project.getPhysicalPath())},
                 'portal_type': 'Iteration',
                 'sort_on': 'start'}
        brains = self.catalog.searchResults(query)
        for brain in brains:
            iterations.append({
                'id': brain.id,
                'uid': brain.UID,
                'title': brain.Title,
                'description': brain.description,
                'available': iteration_context.id != brain.getId,
            })

        self.iterations = iterations
        return self.ch_iteration_template()

    def change_iteration(self):
        """Move the story to the requested iteration
        """
        destination = self.request.get('destination')
        if not destination:
            return json.dumps(False)
        destination = uuidToObject(destination)
        destination.manage_pasteObjects(
            self.context.aq_parent.manage_cutObjects(
                self.context.getId()))

        return json.dumps(True)
