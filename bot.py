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

# Проверяем, загружены ли ключи
if not VK_API_TOKEN:
    print("ОШИБКА: VK_API_TOKEN не найден!")
if not OPENAI_API_KEY:
    print("ОШИБКА: OPENAI_API_KEY не найден!")

# Подключаемся к VK API
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

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
        print(f"ОШИБКА OpenAI: {e}")  # Логируем ошибку в консоли
        return "Извините, у меня возникла ошибка."

# Функция отправки сообщений ВКонтакте
def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
    except Exception as e:
        print(f"ОШИБКА VK API: {e}")  # Логируем ошибку в консоли

# Запускаем прослушивание сообщений в отдельном потоке
import threading

def listen_vk():
    print("Бот запущен и слушает сообщения...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text
            print(f"Получено сообщение от {event.user_id}: {user_message}")  # Логируем сообщение
            
            # Отправляем сообщение в OpenAI
            response = chat_with_gpt(user_message)

            # Отправляем ответ пользователю
            send_message(event.user_id, response)

# Запускаем поток для VK
threading.Thread(target=listen_vk, daemon=True).start()

# Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
