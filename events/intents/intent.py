
from events.speechoutput.response import Response


class LaunchRequest:
    def __init__(self, request):
        self.request = request

    def get_welcome_response(self):

        response_components = {
            'output_speech': 'Welcome to spelling bee! What difficulty would you like; easy,\
                             medium, or hard?',
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get your first word.',
            'should_end_session': False,
            'session_attributes': {'output_type': 'speech'}
        }
        return Response(response_components).build_response()


class IntentRequest:
    def __init__(self, request):
        self.request = request


class SessionEndedRequest:
    def __init__(self, request):
        self.request = request
