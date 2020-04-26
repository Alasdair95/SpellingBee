
import random

from my_words import *

from apis.wordsapi import WordsApi
from apis.isp import InSkillPurchasing
from events.speechoutput.response import Response
from database.storage import Storage


class LaunchRequest:
    def __init__(self, request, user_item):
        self.request = request
        self.session_attributes = {
            'output_type': 'speech',
            'user_item': user_item,
            'num_correct_in_row': 0,
            'mode': 'regular'
        }

    def get_welcome_response(self):
        if 'name' in self.session_attributes['user_item'].keys():
            name = self.session_attributes['user_item']['name']['S']
            output_speech = f'Welcome back {name}! What difficulty would you like; easy, medium, or hard?'
        else:
            output_speech = 'Welcome to spelling bee! What difficulty would you like; easy, medium, or hard?'

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get your first word.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()


class IntentRequest:
    def __init__(self, request, session, context):
        self.request = request
        self.session = session
        self.context = context
        self.session_attributes = session['attributes']
        self.intent_mapping = {
            'AMAZON.FallbackIntent': (self.handle_bad_request, False),
            'AMAZON.CancelIntent': (self.end_session, False),
            'AMAZON.StopIntent': (self.end_session, False),
            'AMAZON.HelpIntent': (self.help_request, False),
            'difficultyLevel': (self.get_first_word_of_session, False),
            'letterAttempt': (self.handle_word_spelling, False),
            'newWord': (self.get_new_word, False),
            'getWordDefinition': (self.get_word_definition, True),
            'getExampleSentence': (self.get_example_sentence, True),
            'listInSkillProducts': (self.list_in_skill_products, False),
            'buyPremium': (self.buy_premium, False),
            'describePremiumContent': (self.describe_premium_content, False),
            'cancelSubscription': (self.cancel_subscription, True),
            'isUserPremium': (self.is_user_premium, False),
            'getPersonalBest': (self.get_personal_best, True),
            'getUserName': (self.set_user_name, True),
            'typeOfWord': (self.get_word_type, True),
            'wordReminder': (self.word_reminder, False),
            'activateHomeworkMode': (self.activate_homework_mode, True),
            'deactivateHomeworkMode': (self.deactivate_homework_mode, True),
            'addHomeworkWord': (self.add_homework_word, True),
            'clearHomeworkList': (self.clear_homework_list, True),
            'listHomeworkWords': (self.list_homework_words, True)
        }

    def return_response(self):
        intent_triggered = self.request['intent']['name']
        method_tuple = self.intent_mapping.get(intent_triggered)

        if method_tuple[1]:
            if self.premium_user_check():
                try:
                    return method_tuple[0]()
                except Exception as e:
                    print(e)
                    return self.handle_bad_request()
            else:
                response_components = {
                    'output_speech': 'That is a premium function. Ask Alexa about what you can buy in this skill'
                                     ' to find out more.',
                    'card': '',
                    'reprompt_text': 'Say Alexa, what can I buy',
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()
        else:
            try:
                return method_tuple[0]()
            except Exception as e:
                print(e)
                return self.handle_bad_request()

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
            else:
                word_list = hard

            word = word_list[random.randint(0, len(word_list) - 1)]

            self.session_attributes['difficulty_level'] = difficulty_level
            self.session_attributes['word'] = word.lower()
            self.session_attributes['attempt_number'] = 0

            word_letter_list = [i for i in word]
            count = 1

            for letter in word_letter_list:
                self.session_attributes[f'letter_{count}'] = letter
                count += 1

            response_list = [f'Your word is: {word}',
                             f'Your first word is: {word}']

            output_speech = response_list[random.randint(0, len(response_list) - 1)]

            response_components = {
                'output_speech': output_speech,
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
            letter_given = slot_dict['value'].lower().replace('.', '')

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
                    num_correct_in_row = self.session_attributes['num_correct_in_row']
                    self.session_attributes['num_correct_in_row'] = num_correct_in_row + 1

                    if (self.session_attributes['num_correct_in_row'] >
                            int(self.session_attributes['user_item']['personalBest']['N'])):
                        storage = Storage(self.context, self.request)
                        storage.update_personal_best(self.session_attributes['num_correct_in_row'])

                    response_components = {
                        'output_speech': f"Well done, you spelled the word {self.session_attributes['word']} correctly."
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
                self.session_attributes['num_correct_in_row'] = 0
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
            slot_value = slot_dict['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']

            if slot_value == 'yes':
                if self.session_attributes['difficulty_level'] == 'easy':
                    word_list = easy
                elif self.session_attributes['difficulty_level'] == 'medium':
                    word_list = medium
                else:
                    word_list = hard

                word = word_list[random.randint(0, len(word_list) - 1)]

                self.session_attributes['word'] = word.lower()
                self.session_attributes['attempt_number'] = 0

                keys_to_pop = []
                for key in self.session_attributes.keys():
                    if key.startswith('letter'):
                        keys_to_pop.append(key)

                for key in keys_to_pop:
                    self.session_attributes.pop(key, None)

                word_letter_list = [i for i in word]
                count = 1

                for letter in word_letter_list:
                    self.session_attributes[f'letter_{count}'] = letter
                    count += 1

                response_list = [f'Your word is: {word}',
                                 f'Your next word is: {word}',
                                 f'Your new word is: {word}',
                                 f'Your next word to spell is: {word}']

                output_speech = response_list[random.randint(0, len(response_list) - 1)]

                response_components = {
                    'output_speech': output_speech,
                    'card': '',
                    'reprompt_text': f'Your word is: {word}',
                    'should_end_session': False,
                    'session_attributes': self.session_attributes
                }
                return Response(response_components).build_response()
            else:
                return self.end_session()

    def get_word_definition(self):
        if 'word' in self.session_attributes.keys():
            words_api = WordsApi(self.session_attributes)
            return words_api.get_word_definition()
        else:
            response_components = {
                'output_speech': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'card': '',
                'reprompt_text': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def get_example_sentence(self):
        if 'word' in self.session_attributes.keys():
            words_api = WordsApi(self.session_attributes)
            return words_api.get_example_sentence()
        else:
            response_components = {
                'output_speech': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'card': '',
                'reprompt_text': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def get_word_type(self):
        if 'word' in self.session_attributes.keys():
            words_api = WordsApi(self.session_attributes)
            return words_api.get_word_type()
        else:
            response_components = {
                'output_speech': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'card': '',
                'reprompt_text': 'You need to get a word first. Say easy, medium, or hard to'
                                 ' pick a difficulty.',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def help_request(self):
        self.session_attributes['output_type'] = 'speech'
        response_components = {
            'output_speech': 'Say easy, medium, or hard, to pick the level of difficulty and get a new word.',
            'card': '',
            'reprompt_text': 'Say easy, medium, or hard, to pick the level of difficulty and get a new word.',
            'should_end_session': False,
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

    def describe_premium_content(self):
        if self.session_attributes['user_item']['premium']['BOOL']:
            output_speech = 'Buying Premium gives you access to everything in this skill. '\
                            'You can ask for word definitions and example sentences. '\
                            'There is homework mode where you create your own list of words to spell.'\
                            'Alexa will also remember your name as well as more functionality you can find on the '\
                            'Spelling Bee skill page.'
        else:
            output_speech = 'Buying Premium gives you access to everything in this skill. '\
                             'You can ask for word definitions and example sentences. '\
                             'There is homework mode where you create your own list of words to spell.'\
                             'Alexa will also remember your name as well as more functionality you can find on the '\
                             'Spelling Bee skill page. '\
                             'Tell Alexa you want to buy premium to get started.'\

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': 'Say Alexa, buy premium to get access to all of the premium content.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def cancel_subscription(self):
        isp = InSkillPurchasing(self.context, self.request, self.session_attributes)
        return isp.cancel_subscription()

    def is_user_premium(self):
        try:
            if self.session_attributes['user_item']['premium']['BOOL']:
                output_speech = 'Yes, you are a premium user.'
            else:
                output_speech = 'No, you\'re not a premium user. Ask Alexa to buy premium to get started.'
        except Exception:
            output_speech = 'No, you\'re not a premium user. Ask Alexa to buy premium to get started.'

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': 'Say Alexa, what is premium, to hear about the premium subscription.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def get_personal_best(self):
        storage = Storage(self.context, self.request)
        user_item = storage.get_user_item()
        self.session_attributes['user_item'] = user_item
        personal_best = user_item['personalBest']['N']

        if personal_best == '0':
            output_speech = 'You don\'t have a record yet. Say easy, medium or hard to get a word to spell.'
        elif personal_best > '1':
            output_speech = f'Your personal best is spelling {personal_best} words in a row.'
        else:
            output_speech = f'Your personal best is spelling {personal_best} word correctly.'

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get a word and keep spelling.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def set_user_name(self):
        storage = Storage(self.context, self.request)
        storage.set_user_name()
        name = self.request['intent']['slots']['UserName']['value'].title()

        response_components = {
            'output_speech': f'Ok {name}, I\'ll remember that for next time. Ask Alexa to tell you about premium'
                             f' or visit the Spelling Bee skill page to find out about all of the premium content.',
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get a word and keep spelling.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def word_reminder(self):
        if 'word' in self.session_attributes.keys():
            word = self.session_attributes['word']

            response_list = [f'Your word is: {word}',
                             f'Your current word is: {word}',
                             f'Your current word to spell is: {word}',
                             f'Your word to spell is: {word}']

            output_speech = response_list[random.randint(0, len(response_list) - 1)]

        else:
            output_speech = 'You don\'t currently have a word. Say easy, medium or hard to get started.'

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': output_speech,
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def activate_homework_mode(self):
        self.session_attributes['mode'] = 'homework'
        homework_list = [i['S'] for i in self.session_attributes['user_item']['homeworkList']['L']]

        word = homework_list[random.randint(0, len(homework_list) - 1)]

        self.session_attributes['word'] = word.lower()
        self.session_attributes['attempt_number'] = 0

        word_letter_list = [i for i in word]
        count = 1

        for letter in word_letter_list:
            self.session_attributes[f'letter_{count}'] = letter
            count += 1

        response_components = {
            'output_speech': f'Homework mode activated. Your first word is: {word}',
            'card': '',
            'reprompt_text': None,
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def deactivate_homework_mode(self):
        self.session_attributes['mode'] = 'regular'

        response_components = {
            'output_speech': f'Homework mode deactivated. Say easy, medium, or hard to get a new word.',
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get a word and start spelling again.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def add_homework_word(self):
        slot_dict = self.request['intent']['slots'].get('HomeworkWord', None)
        if not slot_dict:
            return self.handle_bad_request()
        else:
            new_word = slot_dict['value'].lower()
            homework_list = self.session_attributes['user_item']['homeworkList']['L']
            homework_list.append({'S': new_word})
            storage = Storage(self.context, self.request)
            storage.add_homework_word(homework_list)

            response_components = {
                'output_speech': f'I\'ve added the word: {new_word} to your homework list.',
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def clear_homework_list(self):
        homework_list = []
        storage = Storage(self.context, self.request)
        storage.add_homework_word(homework_list)

        response_components = {
            'output_speech': 'I\'ve emptied your homework list. You can now start adding new words to it again.',
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get a word and start spelling again.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def list_homework_words(self):
        homework_list = [i['S'] for i in self.session_attributes['user_item']['homeworkList']['L']]
        homework_list[-1] = 'and '+homework_list[-1]
        words_string = ', '.join(homework_list)

        if len(homework_list) == 0:
            output_speech = 'You don\'t have any words in your homework list yet. ' \
                            'Say Alexa, add word to my homework list.'
        elif len(homework_list) == 1:
            output_speech = f'Your homework list has the word {words_string.replace("and", "").strip()} in it.'
        else:
            output_speech = f'Your homework list has these words: {words_string}'

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': 'Pick easy, medium, or hard to get a word and start spelling again.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()


class ConnectionsResponse:
    def __init__(self, request, user_item, context, session):
        self.request = request
        self.context = context
        self.session = session
        self.session_attributes = {
            'output_type': 'speech',
            'user_item': user_item
        }

    def get_welcome_back_response(self):
        if self.request['name'] == 'Buy':
            storage = Storage(self.context, self.request)
            storage.update_user_to_premium()
            self.session_attributes['user_item']['premium']['BOOL'] = True
            response_components = {
                'output_speech': 'Thanks for buying premium, you now have access to all of the premium content. '
                                 'Say: Alexa, set my name as, and then say your name.',
                'card': '',
                'reprompt_text': 'Ask Alexa to describe the premium content.',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()
        else:
            storage = Storage(self.context, self.request)
            storage.remove_access_to_premium()
            self.session_attributes['user_item']['premium']['BOOL'] = False
            response_components = {
                'output_speech': 'Say easy, medium, or hard to get a word and start spelling',
                'card': '',
                'reprompt_text': 'Ask Alexa to describe the premium content.',
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()
