# -*- coding: utf-8 -*-
import os
import datetime
import random

from flask import Flask, request, jsonify, render_template
from slack_sdk import WebClient

from config import slack_token, e_user, e_pass, openaikey
from resavepermission import *
from answers import answers

import openai
import time
import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import logging



logging.basicConfig(filename='inna.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



app = Flask(__name__)
lock = threading.Lock()

answered_messages = {}
openai.api_key = openaikey

api_token = slack_token

syscontent = "Отвечай всегда с юмором"  # Глобальная переменная для системного контента

def check_screenshot_result(screenshot_path):
    if os.path.exists(screenshot_path):
        return True
    return False

current_time = datetime.datetime.now()
datetime_str = current_time.strftime("%d-%m-%Y_%H-%M-%S")
screenshot_path = f"screens/screenshot_{datetime_str}.png"  # Путь для сохранения скриншота

def capture_screenshot_with_sort(output_path):
    logging.info('capture_screenshot_with_sort will started')
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://yclients.helpdeskeddy.com/ru/ticket/list/filter/id/17/page/1")

        username_input = driver.find_element(By.ID, "login")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(e_user)
        password_input.send_keys(e_pass)
        password_input.send_keys(Keys.ENTER)
        driver.set_window_size(900, 600)
        time.sleep(10)

        sort_button = driver.find_element(By.XPATH,
                                          ' // *[ @ id = "ticket-app"] / section / section / div[2] / div / div[1] / div[2] / table / thead / tr / th[3]')
        sort_button.click()
        driver.get("https://yclients.helpdeskeddy.com/ru/ticket/list/filter/id/17/page/1")
        time.sleep(10)
        sort_button = driver.find_element(By.XPATH,
                                          ' // *[ @ id = "ticket-app"] / section / section / div[2] / div / div[1] / div[2] / table / thead / tr / th[4]')
        sort_button.click()
        driver.get("https://yclients.helpdeskeddy.com/ru/ticket/list/filter/id/17/page/1")
        time.sleep(5)

        ticket_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="ticket-list-column-title__center"]/a'))
        )

        link = ticket_link.get_attribute('href')
        time.sleep(2)
        driver.save_screenshot(output_path)
        if check_screenshot_result(output_path):
            driver.quit()
            logging.info('ScreenShot Saved Succesfully')
        else:
            logging.info('Error saving screenshot. Run again')
            capture_screenshot_with_sort(screenshot_path)
        return link

    except NoSuchElementException:
        logging.info('WebDriver: NoSuchElementException. Run again')
        capture_screenshot_with_sort(screenshot_path)



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
input_text = "Представь, что ты красивый бот Инна. Расскажи что-то смешное от ее имени."
funny_response = chat_with_model(input_text)
print(funny_response)
print("Iam Alive")

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

    elif message.startswith('!стат'):
        global current_time
        current_time = datetime.datetime.now()
        link = capture_screenshot_with_sort(screenshot_path)
        client.files_upload_v2(channel=channel_id, thread_ts=thread_ts, file=screenshot_path, initial_comment=link)
        return [f"Статистику захотел, дружок? {current_time}"]

    else:
        response = chat_with_model(message)
        return [response]  # Возвращаем список с одним ответом




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inna', methods=['POST'])
def slack_events():
    data = request.get_json()
    if 'event' in data and 'text' in data['event']:
        text = data['event']['text']
        channel_id = data['event']['channel']
        thread_ts = data['event']['ts']
        user = data['event']['user']
        # Используйте регулярное выражение для поиска упоминаний пользователей в тексте
        mentioned_users = re.findall(r'<@(\w+)>', text)

        # Удалите упоминания пользователей из текста
        cleaned_text = re.sub(r'<@(\w+)>', '', text).strip()

        with lock:
            if thread_ts in answered_messages:
                return jsonify({'ok': True})

            response_text = process_message(cleaned_text, data)
            for response in response_text:
                message = f"<@{user}> {response}"  # Добавляем упоминание пользователя в начало текста ответа
                client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=message)

            answered_messages[thread_ts] = time.time()
            current_time = time.time()
            expired_messages = [ts for ts, timestamp in answered_messages.items() if
                                current_time - timestamp > 2 * 60 * 60]
            for ts in expired_messages:
                del answered_messages[ts]
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(port=3000)

