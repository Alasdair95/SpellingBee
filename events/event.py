import json

from events.intents.intent import LaunchRequest, IntentRequest, SessionEndedRequest


class Event:

    def __init__(self, event):
        self.session = event['session']
        self.context = event['context']
        self.request = event['request']

    def get_user_item_from_dynamodb(self):
        # Retrieve the users item from DynamoDB
        # If it is a new user this function needs to call a function that creates a new item and return that item
        pass

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
