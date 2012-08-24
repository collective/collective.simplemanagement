import json

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException


class WFActions(BrowserView):

    @property
    def wf_tool(self):
        return getToolByName(self.context, 'portal_workflow')

    def wf_actions(self):
        """return a list of transition available for the context
        """
        actions = []
        wf = self.wf_tool.getWorkflowsFor(self.context)[0]
        for i in wf.listActionInfos(object=self.context):
            if i['available'] and i['allowed']:
                # TODO: we need this check?
                tr = i['transition']
                actions.append({
                    'destination': tr.new_state_id,
                    'description': tr.description,
                    'id': i['id'],
                    'title': i['title']
                })
        return json.dumps(actions)

    def change_status(self):
        """Perform a workflow transaction
        and return current workflow status"""
        action = self.request.get('action')
        success = True
        try:
            self.wf_tool.doActionFor(self.context, action)
        except WorkflowException:
            success = False
        return json.dumps(success)
