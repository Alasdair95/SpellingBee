import json
from flask import Flask, request

from events.event import Event

app = Flask(__name__)


@app.route("/lambda_function", methods=["GET", "POST"])
def lambda_function():
    event = request.get_json(silent=True, force=True)
    return Event(event)
# This is required for when I am done develop and am ready to deploy
# def lambda_function(event):
#     return Event(event)


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
