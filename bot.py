import telebot
import os

from config import *
from main import *

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Чтобы сгенерировать картинку, Вам нужно прописать /generate [Ваш запрос]')


@bot.message_handler(commands=['generate'])
def generate_command(message: telebot.types.Message):
    try:
        bot.send_message(message.chat.id, "Картинка создается по Вашему запросу. Ожидайте.")
        bot.send_chat_action(message.chat.id, action='upload_photo', timeout=10)

        prompt = message.text[10:]
        image = f"{message.from_user.id}.png"

        base64_to_png(image, generate_image(prompt))

        with open(image, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, f'Фото сгенерировано по запросу: {prompt}')
            os.remove(image)
    except:
        bot.send_message('Не удалось создать картинку. Оплатите подписку.')

bot.polling(non_stop=True)
