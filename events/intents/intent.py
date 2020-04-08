
import random

from my_words import *
from events.speechoutput.response import Response


class LaunchRequest:
    def __init__(self, request, user_item):
        self.request = request
        self.session_attributes = {
            'output_type': 'speech',
            'user_item': user_item
        }

    def get_welcome_response(self):

        response_components = {
            'output_speech': 'Welcome to spelling bee! What difficulty would you like; easy,\
                             medium, or hard?',
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get your first word.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()


class IntentRequest:
    def __init__(self, request, session):
        self.request = request
        self.session_attributes = session['attributes']
        self.intent_mapping = {
            'difficultyLevel': self.get_first_word_of_session()
        }

    def return_response(self):
        intent_triggered = self.request['intent']['name']
        return self.intent_mapping.get(intent_triggered)

    def get_first_word_of_session(self):
        difficulty_level = self.request['intent']['slots']['Difficulty']['value']

        if difficulty_level == 'easy':
            word_list = easy
        elif difficulty_level == 'medium':
            word_list = medium
        else:
            word_list = hard

        word = word_list[random.randint(0, len(word_list))]

        self.session_attributes['difficulty_level'] = difficulty_level
        self.session_attributes['word'] = word
        self.session_attributes['attempt_number'] = 0

        response_components = {
            'output_speech': f'Your first word is {word}',
            'card': '',
            'reprompt_text': f'Your first word is {word}',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()


class SessionEndedRequest:
    def __init__(self, request):
        self.request = request
