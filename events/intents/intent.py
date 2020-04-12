
import random

from my_words import *

from apis.wordsapi import WordsApi
from apis.isp import InSkillPurchasing
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
    def __init__(self, request, session, context):
        self.request = request
        self.context = context
        self.session_attributes = session['attributes']
        self.intent_mapping = {
            'AMAZON.FallbackIntent': self.handle_bad_request,
            'AMAZON.CancelIntent': self.end_session,
            'AMAZON.StopIntent': self.end_session,
            'AMAZON.HelpIntent': self.help_request,
            'difficultyLevel': self.get_first_word_of_session,
            'letterAttempt': self.handle_word_spelling,
            'newWord': self.get_new_word,
            'getWordDefinition': self.get_word_definition,
            'getExampleSentence': self.get_example_sentence,
            'listInSkillProducts': self.list_in_skill_products,
            'buyPremium': self.buy_premium
        }

    def return_response(self):
        intent_triggered = self.request['intent']['name']
        return self.intent_mapping.get(intent_triggered, self.handle_bad_request())()

    def handle_bad_request(self):
        response_components = {
            'output_speech': 'Sorry, could you repeat that please?',
            'card': '',
            'reprompt_text': 'Sorry, could you repeat that please?',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def premium_user_check(self):
        if self.session_attributes['user_item']['premium']['BOOL']:
            return True
        else:
            return False

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
                'output_speech': f'Your word is: {word}',
                'card': '',
                'reprompt_text': f'Your word is: {word}',
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

    def get_word_definition(self):
        if self.premium_user_check():
            if 'word' in self.session_attributes.keys():
                words_api = WordsApi(self.session_attributes)
                return words_api.get_word_definition()
            else:
                response_components = {
                    'output_speech': 'You need to get a word first. Say easy, medium, or hard to'
                                     ' pick a difficulty.',
                    'card': '',
                    'reprompt_text': None,
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()
        else:
            response_components = {
                'output_speech': 'That is a premium function. Ask Alexa about what you can buy in this skill'
                                 ' to find out more',
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def get_example_sentence(self):
        if self.premium_user_check():
            if 'word' in self.session_attributes.keys():
                words_api = WordsApi(self.session_attributes)
                return words_api.get_example_sentence()
            else:
                response_components = {
                    'output_speech': 'You need to get a word first. Say easy, medium, or hard to'
                                     ' pick a difficulty.',
                    'card': '',
                    'reprompt_text': None,
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()
        else:
            response_components = {
                'output_speech': 'That is a premium function. Ask Alexa about what you can buy in this skill'
                                 ' to find out more',
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def help_request(self):
        self.session_attributes['output_type'] = 'speech'
        response_components = {
            'output_speech': 'Say easy, medium, or hard, to pick the level of difficulty and get a new word.',
            'card': '',
            'reprompt_text': None,
            'should_end_session': True,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def end_session(self):
        self.session_attributes['output_type'] = 'speech'
        response_components = {
            'output_speech': 'Thanks for playing Spelling Bee! Goodbye!',
            'card': '',
            'reprompt_text': None,
            'should_end_session': True,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def list_in_skill_products(self):
        isp = InSkillPurchasing(self.context, self.request, self.session_attributes)
        return isp.list_in_skill_products()

    def buy_premium(self):
        isp = InSkillPurchasing(self.context, self.request, self.session_attributes)
        return isp.buy_premium()


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


class ConnectionsResponse:
    def __init__(self, request, user_item):
        self.request = request
        self.session_attributes = {
            'output_type': 'speech',
            'user_item': user_item
        }

    def get_welcome_back_response(self):
        self.session_attributes['user_item']['premium']['BOOL'] = True
        response_components = {
            'output_speech': 'Thanks for buying premium, you now have access to all of the premium content. '
                             'Ask Alexa to describe the premium content or say easy, medium, or hard, to get'
                             ' a new word and start spelling again.',
            'card': '',
            'reprompt_text': 'Ask Alexa to describe the premium content.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()
