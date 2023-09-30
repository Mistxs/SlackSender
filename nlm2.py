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

    # ���������� ��������� �� ������ "Reminder: ����� � 21:00 �������� � ���� ���-�� �������� ����� + ���� ��������� ������ ������� ����"
    messages = response['messages']
    reminder_messages = [msg for msg in messages if msg.get('text') == "Reminder: ����� � 21:00 �������� � ���� ���-�� �������� ����� + ���� ��������� ������ ������� ����"]

    # �������� �� ������� ��������� � ������� ���������� ���������
    if reminder_messages:
        last_message = reminder_messages[-1]
        return last_message
    else:
        return None


def send_reminder(channel_id, message):
    last_message = find_last_reminder_message(channel_id)

    # ���� ���� ��������� ���������, ��������� ����������� ��� ���
    if last_message:
        thread_ts = last_message['ts']
        response = send_to_slack(message, thread_ts)
        return response
    else:
        return None


def daily_reminder():
    # �������� ������� ���� � �����
    current_time = datetime.now()
    target_time = current_time.replace(hour=20, minute=58, second=0, microsecond=0)

    # ���� ������� ����� ����� �������� �������, ���������� �����������
    if current_time == target_time:
        message = "�����������: ����� � 21:00 �������� � ���� ���-�� �������� ����� + ���� ��������� ������ ������� ����"
        send_reminder(channel_id, message)

message = "�����������: ����� � 21:00 �������� � ���� ���-�� �������� ����� + ���� ��������� ������ ������� ����"
send_reminder(channel_id, message)


#
# # ������� ��������� ������ BlockingScheduler
# scheduler = BlockingScheduler()
#
# # ��������� ������ daily_reminder ������ ���� � 20:58
# scheduler.add_job(daily_reminder, 'cron', hour=20, minute=58)
#
# # ��������� �����������
# scheduler.start()