import json
from Products.Five.browser import BrowserView


class StoryMove(BrowserView):

    def __call__(self):
        id_ = self.request.get('story_id')
        position = self.request.get('position')
        if not position.isdigit():
            return json.dumps({
                'success': False,
                'error': 'Position not valid'
            })

        try:
            self.context.moveObject(id_, int(position))
        except:
            return json.dumps({
                'success': False,
                'error': 'An error occurred on moving story'
            })

        return json.dumps({
            'error': None,
            'success': True
        })
