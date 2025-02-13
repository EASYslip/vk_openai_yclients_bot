import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import os
from flask import Flask

# 🔹 Загружаем API-ключи из переменных окружения
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Подключаемся к VK API
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# 🔹 Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# 🔹 Создаем Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# 🔹 Функция общения с ChatGPT
def chat_with_gpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        return "Извините, у меня возникла ошибка."

# 🔹 Функция отправки сообщений ВКонтакте
def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

# 🔹 Поток для VK LongPoll
import threading

def listen_vk():
    print("✅ Бот запущен и слушает сообщения...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text
            user_id = event.user_id

            print(f"📩 Получено сообщение от {user_id}: {user_message}")

            # Отправляем запрос в OpenAI
            response = chat_with_gpt(user_message)
            print(f"💬 Ответ OpenAI: {response}")

            # Отправляем ответ пользователю
            send_message(user_id, response)

# 🔹 Запускаем поток для VK
threading.Thread(target=listen_vk, daemon=True).start()

# 🔹 Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
