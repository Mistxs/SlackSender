# -*- coding: utf-8 -*-
import openai
from config import slack_token, openaikey
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.blocking import BlockingScheduler


# Установите токен доступа к Slack API
slack_token = slack_token
client = WebClient(token=slack_token)
# channel_id = "CCPT7J0GN"  #nightline
# channel_id = "C05974NHZ96"  #innachannel
channel_id = "G01F7R29JUB" #нерабочийfast
openai.api_key = openaikey


# Функция для генерации смешного ответа с помощью OpenAI GPT-3
def generate_funny_response(input_text):
    response = openai.Completion.create(
        engine='text-davinci-003',  # Выбор модели GPT-3
        prompt=input_text,
        temperature=0.7,  # Контроль генерации (чем выше значение, тем более разнообразные ответы)
        max_tokens=200,  # Максимальное количество токенов в ответе
        n=1,  # Количество генерируемых ответов
        stop=None,  # Признак окончания генерации (можете задать свое)
    )

    return response.choices[0].text.strip()
# Пример использования
input_text = "Представь, что ты красивый бот Инна. Расскажи что-то смешное от ее имени."


def getchannel():
    try:
        response = client.conversations_list()
        channels = response["channels"]
        for channel in channels:
            channel_name = channel["name"]
            channel_id = channel["id"]
            print(f"Channel Name: {channel_name}, Channel ID: {channel_id}")

    except SlackApiError as e:
        print(f"Error retrieving channel list: {e.response['error']}")


def getpost():
    try:
        response = client.conversations_history(channel=channel_id)
        messages = response["messages"]
        for message in messages:
            # print(message["text"])
            if message["text"] == "улыбнуло)) хоть что-то приятное за сегодня":
                parent_message_ts = message["ts"]
                comment_text = "Я что, шутка для тебя?"
                # Отправить комментарий в тред (родительское сообщение)
                client.chat_postMessage(channel=channel_id, thread_ts=parent_message_ts, text=comment_text)
                break
    except SlackApiError as e:
        print(f"Error reading messages from Slack: {e.response['error']}")


getpost()