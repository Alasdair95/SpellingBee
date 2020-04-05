
from events.intents.intent import LaunchRequest, IntentRequest, SessionEndedRequest
from database.storage import Storage


class Event:

    def __init__(self, event):
        self.session = event['session']
        self.context = event['context']
        self.request = event['request']

    def get_user_item_from_dynamodb(self):
        storage = Storage(self.context)
        user_item = storage.get_user_item()

        if not user_item:
            user_item = {
                'userId': {'S': self.context['System']['user']['userId']},
                'premium': {'BOOL': False}
            }
            storage.save_user_item(user_item)

        return user_item

    def get_my_response(self):
        if self.request['type'] == 'LaunchRequest':
            return LaunchRequest(self.request).get_welcome_response()
        elif self.request['type'] == 'IntentRequest':
            return IntentRequest(self.request)
        elif self.request['type'] == 'SessionEndedRequest':
            return SessionEndedRequest(self.request)
        else:
            # TODO: Handle anything that makes it to here
            pass


if __name__ == '__main__':
    context = {'System': {'user': {'userId': 'abc124'}}}
    e = {
        'context': context,
        'session': {},
        'request': {}
    }
    event = Event(e)
    event.get_user_item_from_dynamodb()
