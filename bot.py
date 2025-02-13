print("Привет, бот запущен!")

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import os

# Загружаем API-токен из переменных окружения
VK_API_TOKEN = os.getenv("VK_API_TOKEN")

# Подключаемся к VK API
vk_session = vk_api.VkApi(token=VK_API_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Функция отправки сообщений
def send_message(user_id, text):
    vk.messages.send(user_id=user_id, message=text, random_id=0)

# Прослушивание событий
print("Бот запущен и слушает сообщения...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        print(f"Получено сообщение от {event.user_id}: {event.text}")  # Лог в консоли
        send_message(event.user_id, "Привет! Я бот и слышу вас.")