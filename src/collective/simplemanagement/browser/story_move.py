import json
import logging
from Products.Five.browser import BrowserView
from plone.app.uuid.utils import uuidToObject
from ..utils import boolize


class StoryMove(BrowserView):

    def __init__(self, context, request):
        super(StoryMove, self).__init__(context, request)
        self.logger = logging.getLogger('collective.simplemanagement')

    def _get_pasted_id(self, results, story_id):
        new_id = None
        for result in results:
            if result['id'] == story_id:
                new_id = result['new_id']
        if new_id is None:
            raise KeyError(
                "Copy error, original id '%s' not found" % story_id
            )
        return new_id

    def move_in_context(self, story_id, new_position, is_copy):
        if is_copy:
            clipboard = self.context.manage_copyObjects(ids=[story_id])
            story_id = self._get_pasted_id(
                self.context.manage_pasteObjects(clipboard),
                story_id
            )
        self.context.moveObject(story_id, int(new_position))

    def move_to_iteration(self, new_iteration, story_id, new_position, is_copy):
        if is_copy:
            clipboard = self.context.manage_copyObjects(ids=[story_id])
        else:
            clipboard = self.context.manage_cutObjects(ids=[story_id])
        new_iteration = uuidToObject(new_iteration)
        story_id = self._get_pasted_id(
            new_iteration.manage_pasteObjects(clipboard),
            story_id
        )
        new_iteration.moveObject(story_id, int(new_position))

    def process(self):
        story_id = self.request['story_id']
        new_position = self.request['new_position']
        new_iteration = self.request.get('new_iteration', '')
        is_copy = boolize(self.request.get('do_copy', 'false'))
        if not new_position.isdigit():
            raise ValueError("Position '%s' is not a digit" % new_position)
        if not new_iteration:
            self.move_in_context(story_id, new_position, is_copy)
        else:
            self.move_to_iteration(new_iteration, story_id, new_position,
                                   is_copy)
        return {
            'success': True,
            'error': None
        }

    def __call__(self):
        try:
            result = self.process()
        except Exception, e: # pylint: disable=W0703
            self.logger.exception("An error occurred while moving the story")
            result = {
                'success': False,
                'error': str(e)
            }
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(result)
