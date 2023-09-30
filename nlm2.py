from datetime import datetime, timedelta
from slack_sdk import WebClient
from apscheduler.schedulers.blocking import BlockingScheduler
from config import slack_token


channel_id = "C058PJHTDEH" #innatest
def send_to_slack(message, thread_ts):
    client = WebClient(token=slack_token)
    response = client.chat_postMessage(channel=channel_id, thread_ts=thread_ts, text=message)
    assert response["message"]["text"] == message, response
    return response


def find_last_reminder_message(channel_id):
    client = WebClient(token=slack_token)
    response = client.conversations_history(channel=channel_id)

    # Фильтрация сообщений по тексту "Reminder: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"
    messages = response['messages']
    reminder_messages = [msg for msg in messages if msg.get('text') == "Reminder: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"]

    # Проверка на наличие сообщений и возврат последнего сообщения
    if reminder_messages:
        last_message = reminder_messages[-1]
        return last_message
    else:
        return None


def send_reminder(channel_id, message):
    last_message = find_last_reminder_message(channel_id)

    # Если есть последнее сообщение, оставляем комментарий под ним
    if last_message:
        thread_ts = last_message['ts']
        response = send_to_slack(message, thread_ts)
        return response
    else:
        return None


def daily_reminder():
    # Получаем текущую дату и время
    current_time = datetime.now()
    target_time = current_time.replace(hour=20, minute=58, second=0, microsecond=0)

    # Если текущее время равно целевому времени, отправляем напоминание
    if current_time == target_time:
        message = "Напоминание: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"
        send_reminder(channel_id, message)

message = "Напоминание: Ровно в 21:00 прислать в тред кол-во открытых чатов + дату изменения самого старого чата"
send_reminder(channel_id, message)


#
# # Создаем экземпляр класса BlockingScheduler
# scheduler = BlockingScheduler()
#
# # Запускаем задачу daily_reminder каждый день в 20:58
# scheduler.add_job(daily_reminder, 'cron', hour=20, minute=58)
#
# # Запускаем планировщик
# scheduler.start()