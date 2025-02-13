import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import os
import threading
from flask import Flask

print("🚀 Бот запущен!")

# Создаём Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Загружаем API-токены из переменных окружения
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Подключаемся к VK API
try:
    vk_session = vk_api.VkApi(token=VK_API_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    print("✅ Успешное подключение к VK API!")
except Exception as e:
    print(f"❌ Ошибка подключения к VK API: {e}")

# Настраиваем OpenAI API
openai.api_key = OPENAI_API_KEY

# Функция общения с OpenAI
def chat_with_gpt(prompt):
    try:
        print(f"🚀 Отправляем запрос в OpenAI: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response["choices"][0]["message"]["content"]
        print(f"✅ OpenAI ответил: {reply}")
        return reply
    except Exception as e:
        print(f"❌ Ошибка запроса к OpenAI: {e}")
        return "Извините, у меня возникла ошибка."

# Функция отправки сообщений в VK
def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
        print(f"📤 Отправлено сообщение пользователю {user_id}: {text}")
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения в VK: {e}")

# Функция прослушивания сообщений от VK
def listen_vk():
    print("⏳ Бот слушает сообщения...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text
            print(f"📩 Получено сообщение от {event.user_id}: {user_message}")

            # Отправляем сообщение в OpenAI
            response = chat_with_gpt(user_message)

            # Отправляем ответ пользователю
            send_message(event.user_id, response)

# Запускаем прослушивание сообщений в отдельном потоке
threading.Thread(target=listen_vk, daemon=True).start()

# Запускаем Flask-сервер
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
