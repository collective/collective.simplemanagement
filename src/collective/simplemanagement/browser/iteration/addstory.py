from ... import api
from ..forms.ajaxform import AjaxFormAction
from ..story.form import AddStoryQuickForm


class AddStoryAction(AjaxFormAction):

    form_class = AddStoryQuickForm

    def form_action(self, data):
        results = api.content.create_story(
            self.context, data, reindex=False
        )
        return results.unrestrictedTraverse('json/view')()
