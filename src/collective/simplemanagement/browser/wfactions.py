import json

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException


class WFActions(BrowserView):

    wf_actions_template = ViewPageTemplateFile('templates/wf_actions.pt')

    @property
    def wf_tool(self):
        return getToolByName(self.context, 'portal_workflow')

    def wf_actions(self):
        """return a list of transition available for the context
        """
        actions = {}
        ordered_actions = ['start', 'complete', 'suspend', 'reopen']
        wf = self.wf_tool.getWorkflowsFor(self.context)[0]

        for k, v in wf.transitions.items():
            actions[k] = {
                'id': v.id,
                'title': v.title,
                'description': v.description,
                'available': False,
                'destination': v.new_state_id
            }

        for i in wf.listActionInfos(object=self.context):
            if i['available'] and i['allowed']:
                actions[i['id']]['available'] = True

        self.actions = [actions[i] for i in ordered_actions]
        return self.wf_actions_template()

    def change_status(self):
        """Perform a workflow transaction
        and return current workflow status"""
        action = self.request.get('action')
        success = self.request.get('destination')

        try:
            self.wf_tool.doActionFor(self.context, action)
        except WorkflowException:
            success = False
        return json.dumps(success)
