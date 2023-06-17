from flask import Flask, render_template, request, jsonify
from slack_sdk import WebClient

from config import slack_token


app = Flask(__name__)

def send_slack_message(message):

    client = WebClient(token=slack_token)
    response = client.chat_postMessage(
        channel="G01F7R29JUB",
        text=message
    )
    if response["ok"]:
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form['message']
        if message:

            if send_slack_message(message):
                return jsonify({'Response': 'Send to Slack!', 'Message': message})
            else:
                return jsonify({'Response': 'Failed to send to Slack!', 'Message': message})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=4000)

