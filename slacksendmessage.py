from slack_sdk import WebClient
from config import slack_token

channel = "G01F7R29JUB" #нерабочийфаст
# channel = "C058PJHTDEH" #innatest

def send_to_slack(message):
    client = WebClient(token=slack_token)
    response = client.chat_postMessage(channel=channel, text=message)
    assert response["message"]["text"] == message, response
    print(response)
    return response

# message = input("Сообщение: ")

message = '''Уииии, я научилась новому делу! Я теперь могу пересохранять права пользователей! Это так интересно и здОрово! Но пока я не могу сказать, насколько он хорош, поэтому давайте попробуем его на реальных пользовательских примерах! Вы можете использовать команду *`\права`* и указать ссылку на пользователя, чтобы протестировать его и дать мне обратную связь. Ура!
Пример сообщения:
```@InnaBot \права <https://yclients.com/settings/users/edit/543449/12098298/?page=1&amp;editable_length=25#>```'''
send_to_slack(message)