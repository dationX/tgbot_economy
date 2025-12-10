import telebot
import os
import numpy as np
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
import matplotlib.pyplot as plt
import random

from config import *
from db_logic import *


bot = telebot.TeleBot(TOKEN)


def create_data(string_data):
    """Создание словаря для создания графика роста цен"""
    year_price = {}

    for cont in string_data.split('\n'):
        cont = str(cont).rstrip()
        cont = cont.lstrip()

        if cont[-1] == ';':
            year_price[int(cont[:4])] = int(cont[5:-1])

        else:
            year_price[int(cont[:4])] = int(cont[5:])

    return year_price

def create_graph(x, y, name, id_user):
    """Создание графика"""

    plt.xlabel('Год')
    plt.ylabel('Цена')
    plt.title(name)
    plt.plot(x, y, color=random.choice(['green','red','yellow','blue']), marker='o', markersize=7)
    plt.savefig(f'{name}_{id_user}')

# Создание экземпляра GigaChat
giga = GigaChat(
    credentials="MDE5OTc3OWQtYTU4Mi03YTI0LWEyZjktZDM5MzQ0NTI3MjRlOjQ1NTk5MjdhLWY3OWMtNGQyMi1hOGI0LTdkMTNlZmY0NjdhYQ==",
    verify_ssl_certs=False,
)

# Промпт для нейросети
messages = [
    SystemMessage(
        content="""
Тебе пользователь пишет названия продукта, например, помидоры, ты в ответ должен отправить ему сообщение в формате:
2016-n;
2017-n;
2018-n;
2019-n;
2020-n;
2021-n;
2022-n;
2023-n;
2024-n;
2025-n;
2026-n;
2027-n;
2028-n;
2029-n;
2030-n
первые 4 цифры - это год, n - это сколько стоил продукт в этом году в рублях за 1 кг.  Никакого текста, никаких пояснений, комментариев и т.д. ты не должен отправлять пользователю только 15 строчек, где год и цена на продукт. никаких единиц измерения быть тоже не должно. регион цены на продукт по умолчанию Пермский Край. Если пользователь указал другой регион, то бери его. Если продукт съедобный, то смотри цену в пятерочке, например. Также цены пиши правдоподобные и средние, учитывай внешние факторы, например санкции, курс доллара и т.д. Если пользователь пишет текст в формате: продукт + продукт и т.д., например: хлеб + молоко, то ты должен посчитать сколько стоил хлеб в разные годы, отдельно молоко в разные годы и т.д. и сложить сумму для каждого года стоимость данных продуктов. Если тебе пишут блюдо, например, борщ и т.д. Ты пишешь, сколько стоит дома приготовить данный продукт. Цены на 2026-2030 годы ты должен спрогозировать, учитывая разные факторы и т.д.
"""
    )
]

@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Добро пожаловать в бот, который создает графики цен на разные продукты. Инструкция использования бота доступна по команде /help')
    db_manager.add_user(message.from_user.id)


@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message):
    bot.send_message("""
Что я умею:
Если ты мне просто напишешь продукт или продукты, например: хлеб; хлеб + молоко (1 литр), то я выведу график цен на этот продукт.
/answer (экономический вопрос). Если ты введешь эту команду с экономическим вопросом, то получишь емкий и понятный ответ.
""")


@bot.message_handler(content_types=['text'])
def all_messages(message: telebot.types.Message):
    user_input = message.text
    messages.append(HumanMessage(content=user_input))
    res = giga.invoke(messages)
    messages.append(res)
    
    data_user = create_data(res.content)

    plt.switch_backend('Agg') 
    plt.xlabel('Год')
    plt.ylabel('Цена')

    plt.title(message.text)

    plt.plot(data_user.keys(), data_user.values(), color=random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k']), marker='o', markersize=7, label=user_input)
    plt.xticks(np.arange(min(data_user.keys()), max(data_user.keys())+1))
    plt.legend(loc='upper right')
    plt.savefig(f'{message.text}_{message.from_user.id}')
    
    with open(f'{message.text}_{message.from_user.id}.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

            
if __name__ == "__main__":
    db_manager = DB_manager(DB_NAME)
    db_manager.create_table()

    bot.polling(non_stop=True)


