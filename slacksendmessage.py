from slack_sdk import WebClient
from config import slack_token
import eddy_collect

# channel = "C05N85JB0UW" #нерабочийфаст
channel = "C058PJHTDEH" #innatest

def send_to_slack(message):
    client = WebClient(token=slack_token)

    thread_ts = '1695402702.651969'
    response = client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=message)
    assert response["message"]["text"] == message, response
    return response

def collect_data():
    prosrok = eddy_collect.get_prosrok()
    queue = eddy_collect.get_queue()
    open = eddy_collect.get_open()
    expert = eddy_collect.get_expert()
    message = f''':aaaaaa: _[Быстрая линия]_ Просрок - *{prosrok}*

:bender: _[Быстрая линия]_ Очередь - *{queue}*

:cattytiping: _[Быстрая линия]_ Открытые - *{open}*

:axeleshik: _[Быстрая линия]_ Эксперт - *{expert}*'''

    return message

send_to_slack(collect_data())
