# -*- coding: utf-8 -*-
import os
import time
import uuid

import psutil
import openai
import logging
from selenium.webdriver.support.wait import WebDriverWait

from config import slack_token, openaikey
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_MISSED

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import datetime

current_time = datetime.datetime.now()
datetime_str = current_time.strftime("%d-%m-%Y_%H-%M-%S")
screenshot_path = f"screens/screenshot_{datetime_str}.png"  # Путь для сохранения скриншота
MAX_RETRIES = 5
RETRY_DELAY = 5  # Задержка между повторными попытками (в секундах)


# Установите токен доступа к Slack API
slack_token = slack_token
client = WebClient(token=slack_token)
channel_id = "CCPT7J0GN"  # nightline
# channel_id = "C05974NHZ96"  # innachannel
# channel_id = "C058PJHTDEH" # innatest
openai.api_key = openaikey


logging.basicConfig(filename='nlm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

retry_counter = {}  # Словарь для хранения количества попыток выполнения задания

def handle_job_missed(event):
    job_id = event.job_id
    logging.info(f"Missed job: {job_id}")

    if job_id not in retry_counter:
        retry_counter[job_id] = 1
    else:
        retry_counter[job_id] += 1

    if retry_counter[job_id] <= MAX_RETRIES:
        new_job_id = f"{job_id}_{uuid.uuid4()}"
        logging.info(f"Добавление повторного задания через 10 секунд (попытка {retry_counter[job_id]}/{MAX_RETRIES})")
        scheduler.add_job(scheduled_message, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=10),
                          id=new_job_id, args=[job_id])
    else:
        logging.info(f"Достигнуто максимальное количество попыток для задания: {job_id}")

        # Удаление созданного задания
        logging.info(f"Delete job: {job_id}")
        scheduler.remove_job(job_id)



def check_response(response):
    if "messages" in response:
        return True
    return False


def check_screenshot_result(screenshot_path):
    if os.path.exists(screenshot_path):
        return True
    return False


def retry_request(func):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            return func()  # Возвращаем результат выполнения функции
        except Exception as e:
            logging.warning(f"[{datetime.datetime.now()}] Error executing {func.__name__}: {str(e)}")
            logging.info(f"[{datetime.datetime.now()}] Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
            retries += 1

    logging.error(f"[{datetime.datetime.now()}] Maximum retries reached for {func.__name__}")


def capture_screenshot_with_sort(output_path):
    logging.info('capture_screenshot_with_sort will started')
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://yclients.helpdeskeddy.com/ru/ticket/list/filter/id/17/page/1")

        username_input = driver.find_element(By.ID, "login")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys("e.barkovskiy@yclients.tech")
        password_input.send_keys("5!euFIHyjwni")
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


def scheduled_message(trigger_message):
    logging.info('start scheduled_message')
    global current_time
    current_time = datetime.datetime.now()
    try:
        response = retry_request(lambda: client.conversations_history(channel=channel_id))
        if check_response(response):
            messages = response["messages"]
            for message in messages:
                if message["text"] == trigger_message:
                    parent_message_ts = message["ts"]
                    # Создание скриншота
                    link = capture_screenshot_with_sort(screenshot_path)
                    # Отправка комментария в тред (родительское сообщение) с прикрепленным скриншотом
                    # client.chat_postMessage(channel=channel_id, thread_ts=parent_message_ts, text="nlm v0.2 (open A/B testing)")
                    client.files_upload_v2(channel=channel_id, thread_ts=parent_message_ts, file=screenshot_path, initial_comment=link)
                    break
            logging.info('scheduled_message executed successfully')
            # Удаление дополнительных заданий только в случае успешного выполнения
            job_ids_to_remove = [job_id for job_id in retry_counter if job_id != trigger_message]
            for job_id in job_ids_to_remove:
                if job_id != "morning_message":
                    logging.info(f"Delete job: {job_id}")
                    scheduler.remove_job(job_id)
        else:
            raise Exception("Invalid response from Slack API")
    except SlackApiError as e:
        # Логирование ошибки
        logging.error(f"Error reading messages from Slack: {e.response['error']}")
        # Повторное выполнение основного задания
        scheduled_message(trigger_message)

# scheduled_message("Reminder: В 9:00 отправить количество открытых чатов в тред")

# Запуск функций по расписанию
scheduler = BlockingScheduler()
scheduler.add_job(
    lambda: scheduled_message("Reminder: В 9:00 отправить количество открытых чатов в тред"),
    'cron', hour=8, minute=59, id='morning_message')
scheduler.add_job(
    lambda: scheduled_message("Reminder: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"),
    'cron', hour=20, minute=59, id='evening_message')
scheduler.add_listener(handle_job_missed, EVENT_JOB_MISSED)

try:
    scheduler.start()
except KeyboardInterrupt:
    pass
