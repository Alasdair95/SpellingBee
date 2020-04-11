
from events.intents.intent import LaunchRequest, IntentRequest, SessionEndedRequest, ConnectionsResponse
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
                'userId': self.context['System']['user']['userId'],
                'premium': False
            }
            storage.save_user_item(user_item)

        return user_item

    def update_user_to_premium(self):
        storage = Storage(self.context)
        storage.update_user_to_premium()

    def get_my_response(self):
        if self.request['type'] == 'LaunchRequest':
            user_item = self.get_user_item_from_dynamodb()
            return LaunchRequest(self.request, user_item).get_welcome_response()
        elif self.request['type'] == 'IntentRequest':
            return IntentRequest(self.request, self.session, self.context).return_response()
        elif self.request['type'] == 'SessionEndedRequest':
            return SessionEndedRequest(self.request, self.session).end_session()
        elif self.request['type'] == 'Connections.Response':
            user_item = self.get_user_item_from_dynamodb()
            self.update_user_to_premium()
            return ConnectionsResponse(self.request, user_item).get_welcome_back_response()
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
