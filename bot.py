import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import openai
import os
from flask import Flask
import threading
import time

print("🚀 Бот запускается...")

# Создаем Flask-сервер
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

# Загружаем API-токены из переменных окружения
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Проверка, что API-ключи загружены
if not VK_API_TOKEN:
    print("❌ Ошибка: VK_API_TOKEN не найден! Проверьте переменные окружения.")
    exit(1)
if not OPENAI_API_KEY:
    print("❌ Ошибка: OPENAI_API_KEY не найден! Проверьте переменные окружения.")
    exit(1)

# Подключаемся к VK API
try:
    vk_session = vk_api.VkApi(token=VK_API_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    print("✅ Подключение к VK API успешно!")
except Exception as e:
    print(f"❌ Ошибка подключения к VK API: {e}")
    exit(1)

# Настраиваем OpenAI
openai.api_key = OPENAI_API_KEY

# Функция общения с ChatGPT
def chat_with_gpt(prompt):
    try:
        print(f"💬 Отправляем запрос в OpenAI: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_response = response.choices[0].message.content.strip()
        print(f"✅ Ответ от OpenAI: {gpt_response}")
        return gpt_response
    except Exception as e:
        print(f"❌ Ошибка OpenAI: {e}")
        return "Извините, я не могу ответить в данный момент."

# Функция отправки сообщений ВКонтакте
def send_message(user_id, text):
    try:
        vk.messages.send(user_id=user_id, message=text, random_id=0)
        print(f"✅ Сообщение отправлено пользователю {user_id}: {text}")
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения в VK: {e}")

# Функция для прослушивания сообщений
def listen_vk():
    print("✅ Бот запущен и слушает сообщения от ВК...")
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    print(f"📩 Новое сообщение от {event.user_id}: {event.text}")

                    user_message = event.text
                    response = chat_with_gpt(user_message)

                    send_message(event.user_id, response)
                    time.sleep(1.5)  # Защита от спама

        except Exception as e:
            print(f"❌ Ошибка в LongPoll: {e}")
            time.sleep(5)

# **Запускаем только один поток для VK**
if __name__ == "__main__":
    print("✅ Запускаем бота в одном потоке...")
    vk_thread = threading.Thread(target=listen_vk, daemon=True)
    vk_thread.start()

    print("✅ Flask-сервер запущен!")
    app.run(host="0.0.0.0", port=10000)
