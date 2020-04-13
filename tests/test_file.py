
import json

from events.event import Event


def test_launch_request():
    with open('tests/testjson/launch_request_payload.json', 'r') as json_file:
        request = json_file.read()
        request = json.loads(request)

    with open('tests/testjson/launch_request_response.json', 'r') as json_file:
        response = json_file.read()
        response = json.loads(response)

    event = Event(request)

    # The next few lines add in a few bits that amazon add on after the response is sent to them
    actual = {
        'body': event.get_my_response()
    }
    actual['body']['response']['type'] = '_DEFAULT_RESPONSE'
    expected = response

    assert json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)
