
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
                'output_speech': f"One definition for the word {self.session_attributes['word']} is: {definition}.",
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def get_example_sentence(self):
        url = self.url_base + self.session_attributes['word'] + '/examples'
        api_response = requests.get(url, headers=self.headers).json()
        example_sentences = api_response.get('examples', None)

        if example_sentences:
            example = example_sentences[random.randint(0, len(example_sentences)-1)]

            response_components = {
                'output_speech': f"Here's your example sentence: {example}.",
                'card': '',
                'reprompt_text': None,
                'should_end_session': False,
                'session_attributes': self.session_attributes
            }
            return Response(response_components).build_response()

    def get_word_type(self):
        url = self.url_base + self.session_attributes['word']
        api_response = requests.get(url, headers=self.headers).json()
        word_types = list(set([word_info['partOfSpeech'] for word_info in api_response.get('results', None)]))

        if len(word_types) == 1:
            if word_types[0][0] not in ['a', 'e', 'i', 'o', 'u']:
                output_speech = f"The word {self.session_attributes['word']} is a {word_types[0]}."
            else:
                output_speech = f"The word {self.session_attributes['word']} is an {word_types[0]}."
        else:
            if word_types[-1][0] not in ['a', 'e', 'i', 'o', 'u']:
                word_types[-1] = 'or a '+word_types[-1]
                types_str = ', '.join(word_types)
                output_speech = f"The word {self.session_attributes['word']} can be a {types_str}."
            else:
                word_types[-1] = 'or an ' + word_types[-1]
                types_str = ', '.join(word_types)
                output_speech = f"The word {self.session_attributes['word']} can be a {types_str}."

        response_components = {
            'output_speech': output_speech,
            'card': '',
            'reprompt_text': None,
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()


if __name__ == '__main__':
    session_attributes = {'word': 'terrible'}
    words_api = WordsApi(session_attributes)
#     words_api.get_example_sentence()
    words_api.get_word_type()
