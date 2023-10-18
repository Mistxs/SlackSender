# -*- coding: utf-8 -*-
import os
import datetime
import random

from flask import Flask, request, jsonify, render_template, redirect, send_file, Response, send_from_directory
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import slack_token, e_user, e_pass, openaikey
from resavepermission import *
from answers import answers, statanswers
from cheapticket import chticket

import os
import eddy_collect



import openai
import time
import threading



app = Flask(__name__)
lock = threading.Lock()

app.register_blueprint(chticket)

answered_messages = {}
openai.api_key = openaikey

api_token = slack_token

syscontent = "Отвечай всегда с юмором"  # Глобальная переменная для системного контента


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


def chat_with_model(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты - красивый бот с именем Инна"},
            {"role": "system", "content": syscontent},
            {"role": "user", "content": message}
                 ])
    return response.choices[0].message.content

# Пример использования
# input_text = "Ты живая?"
# funny_response = chat_with_model(input_text)
# print(funny_response)
# print("Iam Alive")

client = WebClient(token=api_token)

def process_message(message, data):
    print(message)
    text = data['event']['text']
    channel_id = data['event']['channel']
    thread_ts = data['event']['ts']
    user = data['event']['user']
    if message.startswith(r'\права'):
        link = message[len(r'\права'):]
        print(message)
        if resavepermission(link):
            responses = answers
            response = responses[random.randint(0, len(responses) - 1)]
            return ["Готово", response]  # Возвращаем список с двумя ответами
        else:

            return ["Assistant: что-то пошло не так"]
    elif message.startswith(r'!права'):
        link = message[len(r'!права'):]
        print(message)
        if resavepermission(link):
            responses = answers
            response = responses[random.randint(0, len(responses) - 1)]
            return ["Готово", response]  # Возвращаем список с двумя ответами
        else:
            return ["Assistant: что-то пошло не так"]

    elif message.startswith(r'\характ'):
        global syscontent
        syscontent = message[len(r'\характ '):]
        return ["Assistant: Глобальная переменная syscontent была обновлена."]

    elif message.startswith(r'!лог'):
        url = "https://api.ngrok.com/tunnels"
        headers = {
            'Authorization': 'Bearer 2RfT8Fxl9C6Y05oS0wJuC7vDA2U_7KYjKEEkztqfZGb42eyoP',
            'Ngrok-Version': '2'
        }
        response = requests.request("GET", url, headers=headers).json()
        for item in response["tunnels"]:
            if item["public_url"] == "https://b5898dc6e4bc-8806955829454616363.ngrok-free.app":
                tunnel = item["public_url"]
        return [f"{tunnel}/innalog"]

    elif message.startswith(r'!ссылка'):
        url = "https://api.ngrok.com/tunnels"
        headers = {
            'Authorization': 'Bearer 2RfT8Fxl9C6Y05oS0wJuC7vDA2U_7KYjKEEkztqfZGb42eyoP',
            'Ngrok-Version': '2'
        }
        response = requests.request("GET", url, headers=headers).json()
        for item in response["tunnels"]:
            if item["public_url"] != "https://b5898dc6e4bc-8806955829454616363.ngrok-free.app":
                tunnel = item["public_url"]
        return [f"{tunnel}"]

    elif message.startswith('!боль'):
        link = collect_data()
        responses = statanswers
        response = responses[random.randint(0, len(responses) - 1)]
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=link)
        return [response]

    elif message.startswith('!стат'):
        link = collect_data()
        responses = statanswers
        response = responses[random.randint(0, len(responses) - 1)]
        client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=link)
        return [response]

    else:
        response = chat_with_model(message)
        return [response]  # Возвращаем список с одним ответом



@app.route('/innalog')
def log():
    return render_template('logs.html')

@app.route('/logs')
def get_logs():
    print(request)
    with open('rsfp.log', 'r') as file:
        logs = file.readlines()
    data = []
    for log in logs:
        log_parts = re.split(r' - \w+ - ', log)
        if len(log_parts) >= 2:
            timestamp = log_parts[0]
            message = ' - '.join(log_parts[1:]).strip()
            data.append({'timestamp': timestamp, 'message': message})
    return jsonify(data)

@app.route('/')
def home():
    return render_template('error.html')





# @app.route('/inna', methods=['POST'])
# def slack_events():
#     data = request.get_json()
#     if 'event' in data and 'text' in data['event']:
#         text = data['event']['text']
#         channel_id = data['event']['channel']
#         thread_ts = data['event']['ts']
#         user = data['event']['user']
#         # Используйте регулярное выражение для поиска упоминаний пользователей в тексте
#         mentioned_users = re.findall(r'<@(\w+)>', text)
#
#         # Удалите упоминания пользователей из текста
#         cleaned_text = re.sub(r'<@(\w+)>', '', text).strip()
#
#         with lock:
#             if thread_ts in answered_messages:
#                 return jsonify({'ok': True})
#
#             response_text = process_message(cleaned_text, data)
#             for response in response_text:
#                 message = f"<@{user}> {response}"  # Добавляем упоминание пользователя в начало текста ответа
#                 client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=message)
#
#             answered_messages[thread_ts] = time.time()
#             current_time = time.time()
#             expired_messages = [ts for ts, timestamp in answered_messages.items() if
#                                 current_time - timestamp > 2 * 60 * 60]
#             for ts in expired_messages:
#                 del answered_messages[ts]
#     return jsonify({'ok': True})

@app.route('/inna', methods=['POST'])
def slackValidation():
    data = request.json
    return data["challenge"]


# Роуты для вебстраниц (не действий)
@app.route('/start')
def start():
    return render_template('error.html')


@app.route('/fsr')
def fsr():
    return render_template('error.html')

@app.route('/superloyal')
def superloyal():
    return render_template('error.html')

@app.route('/finance')
def finance():
    return render_template('error.html')

@app.route('/unlock')
def unlocker():
    return render_template('error.html')

@app.route('/inna')
def inna():
    return render_template('error.html')

@app.route('/search')
def tracker():
    return render_template('error.html')


@app.route('/feedback')
def fdb():
    return render_template('error.html')

@app.route('/getcookie')
def getcookie():
    return render_template('error.html')

@app.route('/daydetails')
def overpayed():
    return render_template('error.html')

@app.route('/repairslots')
def repairslots():
    return render_template('error.html')

@app.route('/tools4u')
def t4ulink():
    url = "https://api.ngrok.com/tunnels"
    headers = {
        'Authorization': 'Bearer 2RfT8Fxl9C6Y05oS0wJuC7vDA2U_7KYjKEEkztqfZGb42eyoP',
        'Ngrok-Version': '2'
    }
    response = requests.request("GET", url, headers=headers).json()
    for item in response["tunnels"]:
        if item["public_url"] != "https://b5898dc6e4bc-8806955829454616363.ngrok-free.app":
            tunnel = item["public_url"]
            print(tunnel)
    return redirect(tunnel)

@app.route('/cheapticket')
def cheapticket():
    return render_template('chtikets.html')


@app.route('/mydb.db')
def get_mydb():
    return send_file('C:/Users/mistx/PycharmProjects/Monitor/mydatabase.db', as_attachment=True)



if __name__ == '__main__':
    app.run(port=5000)

