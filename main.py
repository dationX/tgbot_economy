import telebot
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
import random
import matplotlib.pyplot as plt

from config import *


bot = telebot.TeleBot(TOKEN)

user_graphs = {}
counts = {}

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


# Создание экземпляра GigaChat
giga = GigaChat(
    credentials=AUTH_KEY,
    verify_ssl_certs=False,
)

# История чата + промпт для нейросети
messages = [
    SystemMessage(
        content="""
Тебе пользователь пишет названия продукта, например, помидоры, ты в ответ должен отправить ему сообщение в формате:
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
2029-n
первые 4 цифры - это год, n - это сколько стоил продукт в этом году в рублях за 1 кг.  Никакого текста, никаких пояснений, комментариев и т.д. ты не должен отправлять пользователю только 13 строчек, где год и цена на продукт. никаких единиц измерения быть тоже не должно. регион цены на продукт по умолчанию Пермский Край. Если пользователь указал другой регион, то бери его. Если продукт съедобный, то смотри цену в пятерочке, например. Также цены пиши правдоподобные и средние, учитывай внешние факторы, например санкции, курс доллара и т.д. Если пользователь пишет текст в формате: продукт + продукт и т.д., например: хлеб + молоко, то ты должен посчитать сколько стоил хлеб в разные годы, отдельно молоко в разные годы и т.д. и сложить сумму для каждого года стоимость данных продуктов. Если тебе пишут блюдо, например, борщ и т.д. Ты пишешь, сколько стоит дома приготовить данный продукт. Цены с 2017 по 2025 годы должны быть крайне реалистичные. Цены для 2025 ты должен брать с сайта пятерочки и т.д., чтобы они были точно актуальны. Учитывая разные факторы и т.д. Учитывая эти же разные факторы ты должен спрогнозировать цену на продукт с 2026 по 2029 годы. Если пользователь задает вопрос, например, что такое инфляция и т.д. или другой иной вопрос связанный с экономикой, ты должен очень кратко, емко и понятно ответить на него совсем небольшим сообщением. В ответе не используй никакие решетки, зведочки и другие символы для форматирования текста. Если вопрос никак не связан с экономикой, то отправляй один символ 0
"""
    )
]


@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Добро пожаловать в бот, который создает графики цен на разные продукты. Инструкция использования бота доступна по команде /help')
    # db_manager.add_user(message.from_user.id)


@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message):
    bot.send_message(message.chat.id, """
Что я умею:
Если ты мне просто напишешь продукт или продукты, например: хлеб; хлеб + молоко (1 литр), то я выведу график цен на этот продукт.
/answer (экономический вопрос). Если ты введешь эту команду с экономическим вопросом, то получишь емкий и понятный ответ.
""")


@bot.message_handler(commands=['clear'])
def clear_command(message: telebot.types.Message):
    chat_id = message.chat.id
    if chat_id in user_graphs:
        plt.close(user_graphs[chat_id][0])
        del user_graphs[chat_id]
        bot.send_message(chat_id, "Текущий график очищен. Можете добавлять новые продукты.")
    else:
        bot.send_message(chat_id, "У вас пока нет активного графика для очистки.")


@bot.message_handler(commands=['answer'])
def answer_command(message: telebot.types.Message):
    user_input = message.text[8:]
    res = giga.invoke(user_input)
    messages.append(res)
    bot.send_message(message.chat.id, res.content, parse_mode='markdown')


@bot.message_handler(content_types=['text'])
def all_messages(message: telebot.types.Message):
    chat_id = message.chat.id
    user_input = message.text
    filename = f'graph_{chat_id}.png'

    try:
        messages.append(HumanMessage(content=user_input))
        res = giga.invoke(messages)
        messages.append(res)
        
        data_user = create_data(res.content)

        # Создание графика
        if chat_id not in user_graphs:
            plt.switch_backend('Agg')
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title("Рост цен на разные продукты")
            ax.set_xlabel('Год')
            ax.set_ylabel('Цена (руб)')
            ax.grid(True, linestyle='--', alpha=0.7)
            user_graphs[chat_id] = (fig, ax)
        else:
            fig, ax = user_graphs[chat_id]

        # Выбор цвета
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        current_colors = [line.get_color() for line in ax.lines]
        new_colors = []

        if current_colors:
            for col in colors:
                if col not in current_colors:
                    new_colors.append(col)

            color = random.choice(new_colors)
        else:
            color = random.choice(colors)

        # Отрисовка графика
        ax.plot(list(data_user.keys()), list(data_user.values()), color=color, marker='o', markersize=7, label=user_input)
        
        ax.legend(loc='upper left')
        ax.set_xticks(range(min(data_user.keys()), max(data_user.keys())+1))
        
        plt.savefig(filename)
        
        with open(filename, 'rb') as photo:
            bot.send_photo(chat_id, photo)
    except:
        bot.send_message(chat_id, "Попробуйте еще раз или введите корректный запрос! Произошла ошибка при построении или обновлении графика.")
    
    try:
        os.remove(filename)
    except:
        pass 

if __name__ == "__main__":
    bot.polling(non_stop=True)
