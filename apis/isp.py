
import requests

from events.speechoutput.response import Response


class InSkillPurchasing:
    def __init__(self, context, request, session_attributes):
        self.context = context
        self.request = request
        self.session_attributes = session_attributes
        self.premium_product_id = 'amzn1.adg.product.ee2d7eb5-287c-43d5-8d40-84a1e6595e1c'

    def list_in_skill_products(self):
        base_url = self.context['System']['apiEndpoint']
        end_url = '/v1/users/~current/skills/~current/inSkillProducts'

        headers = {
            'Accept-Language': self.request['locale'],
            'Authorization': f'Bearer {self.context["System"]["apiAccessToken"]}'
        }

        response = requests.get(base_url+end_url, headers=headers).json()
        product_name = response['inSkillProducts'][0]['name'].title()
        product_type = response['inSkillProducts'][0]['type'].lower()
        product_description = response['inSkillProducts'][0]['summary']
        response_components = {
            'output_speech': f'You can buy {product_name}. It is a {product_type} purchase'
                             f' with the description: {product_description}.'
                             f' Ask Alexa to tell you about premium to find out more.',
            'card': '',
            'reprompt_text': f'You can buy {product_name}. It is a {product_type} purchase'
                             f' with the description: {product_description}'
                             f' Ask Alexa to tell you about premium to find out more.',
            'should_end_session': False,
            'session_attributes': self.session_attributes
        }
        return Response(response_components).build_response()

    def buy_premium(self):
        response_components = {
            'output_speech': None,
            'card': '',
            'reprompt_text': None,
            'should_end_session': True,
            'session_attributes': self.session_attributes,
            'product_id': self.premium_product_id,
            'directive': 'buy'
        }
        return Response(response_components).build_response()

    def cancel_subscription(self):
        response_components = {
            'output_speech': None,
            'card': '',
            'reprompt_text': None,
            'should_end_session': True,
            'session_attributes': self.session_attributes,
            'product_id': self.premium_product_id,
            'directive': 'cancel'
        }
        return Response(response_components).build_response()
