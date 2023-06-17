from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import slack_token

# Установите ваш токен доступа Slack API
slack_token = slack_token

# Создайте экземпляр WebClient
client = WebClient(token=slack_token)

# ID канала, в котором нужно прочитать сообщения
# channel_id = "C058PJHTDEH"
channel_id = "CCPT7J0GN"
message_ts = "1686765312.326469"
def getpost():
    # Укажите идентификатор сообщения, комментарии к которому нужно удалить
    message_ts = "1686765312.326469"

    # Получите список комментариев к указанному сообщению
    try:
        response = client.conversations_replies(channel=channel_id, ts=message_ts)
        comments = response["messages"]
    except SlackApiError as e:
        print(f"Ошибка при получении комментариев: {e.response['error']}")

    # Пройдитесь по каждому комментарию и удалите их
    for comment in comments:
        try:
            client.chat_delete(channel=channel_id, ts=comment["ts"])
            print(f"Комментарий {comment['ts']} удален")
        except SlackApiError as e:
            print(f"Ошибка при удалении комментария {comment['ts']}: {e.response['error']}")


# Удаление сообщений
def delete_messages(channel_id, thread_ts):
    try:
        # Вызов метода chat_delete() для удаления сообщений
        response = client.chat_delete(
            channel=channel_id,
            ts=thread_ts
        )
        if response["ok"]:
            print("Сообщения успешно удалены!")
        else:
            print("Ошибка при удалении сообщений.")
    except SlackApiError as e:
        print("Ошибка при вызове Slack API:", e.response["error"])


getpost()