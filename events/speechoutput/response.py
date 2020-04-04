# This file will contain the functions that build the response dict that will be sent back to Alexa


class Response:
    def __init__(self, response_components):
        self.output_speech = response_components['output_speech']
        self.card = response_components['card']
        self.reprompt_text = response_components['reprompt_text']
        self.should_end_session = response_components['should_end_session']
        self.session_attributes = response_components['session_attributes']

    # Function that builds speech response
    def _build_speech_response(self):
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': self.output_speech
            },
            # TODO: Add field for 'card'
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': self.reprompt_text
                }
            },
            'shouldEndSession': self.should_end_session
        }

    # Function that builds response that can include audio
    def _build_audio_response(self):
        return {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': self.output_speech
            },
            # TODO: Add field for 'card'
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': self.reprompt_text
                }
            },
            'shouldEndSession': self.should_end_session
        }

    # Builds response and sends it back to Alexa
    def build_response(self):

        if self.session_attributes['output_type'] == 'speech':
            response = self._build_speech_response()
        else:
            response = self._build_audio_response()

        return {
            'version': '1.0',
            'sessionAttributes': self.session_attributes,
            'response': response
        }
