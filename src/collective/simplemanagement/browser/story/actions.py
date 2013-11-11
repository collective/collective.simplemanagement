import json
import plone.api
from Acquisition import aq_parent
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ... import api


class Actions(BrowserView):

    template = ViewPageTemplateFile('templates/actions.pt')
    # iterations_template = ViewPageTemplateFile(
    #     'templates/ch_iteration_actions.pt'
    # )

    def wf_actions(self):
        """return a list of transition available for the context
        """
        actions = {}
        ordered_actions = ['start', 'complete', 'suspend', 'reopen']
        wft = plone.api.portal.get_tool(name='portal_workflow')

        wf = wft.getWorkflowsFor(self.context)[0]

        for k, v in wf.transitions.items():
            actions[k] = {
                'id': v.id,
                'title': v.title,
                'description': v.description,
                'available': False,
                'destination': v.new_state_id,
                'href': (
                    '{0}/json/change_status?action='
                    '{1}&destination={2}').format(
                        self.context.absolute_url(),
                        v.id,
                        v.new_state_id
                    )
            }

        for i in wf.listActionInfos(object=self.context):
            if i['available'] and i['allowed']:
                actions[i['id']]['available'] = True

        self.klass = "wf_actions"
        self.actions = [actions[i] for i in ordered_actions]
        return self.template()

    def ch_iteration(self):
        """return a list of iterations available for the context
        """
        iterations = []
        pc = plone.api.portal.get_tool(name='portal_catalog')
        iteration_context = aq_parent(aq_inner(self.context))
        project = api.content.get_project(self.context)
        query = {'path': {'query': '/'.join(project.getPhysicalPath())},
                 'portal_type': 'Iteration',
                 'sort_on': 'start'}
        brains = pc.searchResults(query)
        for brain in brains:
            iterations.append({
                'id': brain.id,
                'uid': brain.UID,
                'title': brain.Title,
                'description': brain.description,
                'available': iteration_context.id != brain.getId,
                'href': '{0}/json/change_iteration?destination={1}'.format(
                    self.context.absolute_url(),
                    brain.UID
                )
            })

        self.actions = iterations
        self.klass = "ch_iteration"
        return self.template()
