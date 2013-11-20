import json
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView


class Helper(BrowserView):

    def json_messages(self):
        messages = {
            'permanent': [],
            'transient': []
        }
        for message in IStatusMessage(self.request).show():
            target = messages['transient']
            if message.type.lower() == 'error':
                target = messages['permanent']
            target.append({
                'type': message.type.lower(),
                'message': message.message
            })
        return json.dumps(messages)
