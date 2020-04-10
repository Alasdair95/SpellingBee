
import os
import requests
import random

from events.speechoutput.response import Response


class WordsApi:
    def __init__(self, session_attributes):
        self.url_base = 'https://wordsapiv1.p.rapidapi.com/words/'
        self.headers = {
            'x-rapidapi-host': 'wordsapiv1.p.rapidapi.com',
            'x-rapidapi-key': os.environ.get('RAPID_API_KEY')
        }
        self.session_attributes = session_attributes
        self.session_attributes['output_type'] = 'speech'

    def get_word_definition(self):
        url = self.url_base + self.session_attributes['word'] + '/definitions'

        api_response = requests.get(url, headers=self.headers).json()

        definitions = api_response.get('definitions', None)

        if definitions:
            definition = definitions[random.randint(0, len(definitions)-1)]['definition']

            response_components = {
                'output_speech': f"One definition for the word {self.session_attributes['word']} is {definition}.",
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()


# if __name__ == '__main__':
#     session_attributes = {'attributes': {'word': 'dog'}}
#     words_api = WordsApi(session_attributes)
#     words_api.get_word_definition()
