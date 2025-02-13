print("Привет, бот запущен!")

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import os
import requests
import threading
from flask import Flask

# Создаем Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Загружаем API-ключи из .env
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка токена VK API
def check_vk_token():
    url = "https://api.vk.com/method/users.get"
    params = {
        "access_token": VK_API_TOKEN,
        "v": "5.131"
    }
    response = requests.get(url, params=params).json()
    
    if "error" in response:
        print(f"Ошибка VK API: {response['error']['error_msg']}")
        return False
    print("✅ VK API токен рабочий!")
    return True

if not check_vk_token():
    exit()  # Если токен невалидный, останавливаем бота

# Подключаемся к VK API
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Принудительное обновление LongPoll
vk_session.http.get("https://api.vk.com/method/messages.getLongPollServer", params={"access_token": VK_API_TOKEN, "v": "5.131"})

# Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# Функция общения с ChatGPT
def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Извините, у меня возникла ошибка."

# Функция отправки сообщений в ВК
def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

# Функция прослушивания событий VK
def listen_vk():
    print("Бот запущен и слушает сообщения...")
    longpoll.update_longpoll_server()  # Принудительно обновляем LongPoll
    
    for event in longpoll.listen():
        print(f"🔄 Получено событие: {event}")  # Лог всех событий

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text
            print(f"📩 Сообщение от {event.user_id}: {user_message}")  # Лог в консоли

            # Получаем ответ от OpenAI
            response = chat_with_gpt(user_message)

            # Отправляем ответ пользователю
            send_message(event.user_id, response)

# Запускаем поток для VK
threading.Thread(target=listen_vk, daemon=True).start()

# Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
