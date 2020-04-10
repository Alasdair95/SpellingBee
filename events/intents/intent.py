
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
            'difficultyLevel': self.get_first_word_of_session(),
            'letterAttempt': self.handle_word_spelling(),
            'newWord': self.get_new_word()
        }

    def return_response(self):
        intent_triggered = self.request['intent']['name']
        # This is where the check for whether the user is premium needs to go
        # If user is not premium we will return another function I need to write - user_not_premium_response
        return self.intent_mapping.get(intent_triggered, self.handle_bad_request())

    def handle_bad_request(self):
        response_components = {
            'output_speech': 'Sorry, could you repeat that please?',
            'card': '',
            'reprompt_text': 'Sorry, could you repeat that please?',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def get_first_word_of_session(self):
        slot_dict = self.request['intent']['slots'].get('Difficulty', None)

        if not slot_dict:
            self.handle_bad_request()
        else:
            difficulty_level = slot_dict['value']

            if difficulty_level == 'easy':
                word_list = easy
            elif difficulty_level == 'medium':
                word_list = medium
            elif difficulty_level == 'hard':
                word_list = hard
            else:  # TODO: Handle anything that gets to here with handle_bad_request when built
                pass

            word = word_list[random.randint(0, len(word_list)-1)]

            self.session_attributes['difficulty_level'] = difficulty_level
            self.session_attributes['word'] = word.lower()
            self.session_attributes['attempt_number'] = 0

            word_letter_list = [i for i in word]
            count = 1

            for letter in word_letter_list:
                self.session_attributes[f'letter_{count}'] = letter
                count += 1

            response_components = {
                'output_speech': f'Your word is {word}',
                'card': '',
                'reprompt_text': f'Your word is {word}',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def handle_word_spelling(self):
        slot_dict = self.request['intent']['slots'].get('Letter', None)
        if not slot_dict:
            return self.handle_bad_request()
        elif slot_dict['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == 'ER_SUCCESS_NO_MATCH':
            return self.handle_bad_request()
        else:
            attempt_number = self.session_attributes['attempt_number'] + 1
            self.session_attributes['attempt_number'] = attempt_number
            letter_required = self.session_attributes[f'letter_{attempt_number}']
            letter_given = slot_dict['value'].lower()

            if letter_given == letter_required:
                if attempt_number < len(self.session_attributes['word']):
                    self.session_attributes['output_type'] = 'audio'
                    response_components = {
                        'output_speech': "<speak><audio src='soundbank://soundlibrary/ui/gameshow/"
                                         "amzn_ui_sfx_gameshow_positive_response_01'/></speak>",
                        'card': '',
                        'reprompt_text': None,
                        'should_end_session': False,
                        'session_attributes': self.session_attributes
                    }
                    return Response(response_components).build_response()
                else:
                    self.session_attributes['output_type'] = 'speech'
                    response_components = {
                        'output_speech': f"Well done, you spelled {self.session_attributes['word']} correctly."
                                         f" Do you want a new word?",
                        'card': '',
                        'reprompt_text': 'Do you want a new word?',
                        'should_end_session': False,
                        'session_attributes': self.session_attributes
                    }
                    return Response(response_components).build_response()
            else:
                self.session_attributes['output_type'] = 'speech'
                attempt_number = self.session_attributes['attempt_number'] - 1
                self.session_attributes['attempt_number'] = attempt_number
                response_components = {
                    'output_speech': "Try again.",
                    'card': '',
                    'reprompt_text': 'Have another go.',
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()

    def get_new_word(self):
        slot_dict = self.request['intent']['slots'].get('YesNo', None)

        if not slot_dict:
            self.handle_bad_request()
        else:
            slot_value = slot_dict['value']

            if slot_value == 'yes':
                if self.session_attributes['difficulty_level'] == 'easy':
                    word_list = easy
                elif self.session_attributes['difficulty_level'] == 'medium':
                    word_list = medium
                elif self.session_attributes['difficulty_level'] == 'hard':
                    word_list = hard
                else:  # TODO: Handle anything that gets to here with handle_bad_request when built
                    pass

                word = word_list[random.randint(0, len(word_list) - 1)]

                self.session_attributes['word'] = word.lower()
                self.session_attributes['attempt_number'] = 0

                word_letter_list = [i for i in word]
                count = 1

                for letter in word_letter_list:
                    self.session_attributes[f'letter_{count}'] = letter
                    count += 1

                response_components = {
                    'output_speech': f'Your word is {word}',
                    'card': '',
                    'reprompt_text': f'Your word is {word}',
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()
            else:
                pass


class SessionEndedRequest:
    def __init__(self, request, session):
        self.request = request
        self.session_attributes = session['attributes']

    def end_session(self):
        self.session_attributes['output_type'] = 'speech'
        response_components = {
            'output_speech': 'Thanks for playing Spelling Bee!',
            'card': '',
            'reprompt_text': None,
            'should_end_session': True,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()
