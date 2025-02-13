print("Привет, бот запущен!")

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import os
from flask import Flask

# Создаем Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Загружаем API-токены из переменных окружения
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Подключаемся к VK API
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# Функция общения с ChatGPT
import openai

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY  # Передаём API-ключ напрямую
    )
    return response["choices"][0]["message"]["content"]

# Функция отправки сообщений ВКонтакте
def send_message(user_id, text):
    vk.messages.send(user_id=user_id, message=text, random_id=0)

# Запускаем прослушивание сообщений в отдельном потоке
import threading

def listen_vk():
    print("Бот запущен и слушает сообщения...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text
            print(f"Получено сообщение от {event.user_id}: {user_message}")  # Лог в консоли
            
            # Отправляем сообщение в OpenAI
            response = chat_with_gpt(user_message)

            # Отправляем ответ пользователю
            send_message(event.user_id, response)

# Запускаем поток для VK
threading.Thread(target=listen_vk, daemon=True).start()

# Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
