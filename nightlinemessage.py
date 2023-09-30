# -*- coding: utf-8 -*-
import time
import uuid

import logging

from config import slack_token, openaikey
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_MISSED

import datetime
import eddy_collect


MAX_RETRIES = 5
RETRY_DELAY = 5  # Задержка между повторными попытками (в секундах)


slack_token = slack_token
client = WebClient(token=slack_token)


channel_id = "CCPT7J0GN"  # nightline
# channel_id = "C05974NHZ96"  # innachannel
# channel_id = "C058PJHTDEH" # innatest


logging.basicConfig(filename='nlm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

retry_counter = {}  # Словарь для хранения количества попыток выполнения задания



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

def check_response(response):
    if "messages" in response:
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
                    # link = capture_screenshot_with_sort(screenshot_path)
                    # Отправка комментария в тред (родительское сообщение) с прикрепленным скриншотом
                    link = collect_data()
                    client.chat_postMessage(channel=channel_id, thread_ts=parent_message_ts, text=link)
                    # client.files_upload_v2(channel=channel_id, thread_ts=parent_message_ts, file=screenshot_path, initial_comment=link)
                    break
            logging.info('scheduled_message executed successfully')
            # Удаление дополнительных заданий только в случае успешного выполнения
            # job_ids_to_remove = [job_id for job_id in retry_counter if job_id != trigger_message]
            # for job_id in job_ids_to_remove:
            #     if job_id != "morning_message":
            #         logging.info(f"Delete job: {job_id}")

        else:
            raise Exception("Invalid response from Slack API")
    except SlackApiError as e:
        # Логирование ошибки
        logging.error(f"Error reading messages from Slack: {e.response['error']}")
        # Повторное выполнение основного задания
        scheduled_message(trigger_message)
#
scheduled_message("Reminder: В 9:00 отправить количество открытых чатов в тред")
scheduled_message("Reminder: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата")

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
