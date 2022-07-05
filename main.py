from pyrogram import Client, filters
from wordcloud import WordCloud
from PIL import Image
from datetime import datetime
from collections import Counter
import config
import re
import numpy

tg_user_bot = Client(
    "my_grabber_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    phone_number=config.PHONE_NUMBER,
)

STOPWORDS_RU = []

with open('STOPWORDS_RU.txt', 'r') as filehandle:
    filelines = filehandle.readlines()
    for line in filelines:
        current_word = line[:-1]
        STOPWORDS_RU.append(current_word)

STAT_CHANNEL_CURRENT = ''

EN_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

NUMBERS = '0123456789'


def split_word(text):
    text = re.sub(r'[^\w\s]', ' ', text)
    text = text.replace('\n', ' ')
    text = re.sub(' +', ' ', text)
    text_changed = ''
    for letter in text:
        if (letter not in EN_ALPHABET) and (letter not in NUMBERS):
            text_changed = text_changed + letter
    lst = text_changed.split()
    for word in STOPWORDS_RU:
        while word in lst:
            lst.remove(word)
        while word.capitalize() in lst:
            lst.remove(word.capitalize())
    return lst


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("add_stopwords"))
def add_stopwords(client, message):
    add_word = (message.text.split())[1]
    STOPWORDS_RU.append(add_word)
    with open('STOPWORDS_RU.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % words for words in STOPWORDS_RU)
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, f"Слово {add_word} успешно добавлено в список.")


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("delete_stopwords"))
def delete_stopwords(client, message):
    delete_word = (message.text.split())[1]
    while delete_word in STOPWORDS_RU:
        STOPWORDS_RU.remove(delete_word)
    with open('STOPWORDS_RU.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % words for words in STOPWORDS_RU)
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, f"Слово {delete_word} успешно удалено из списка.")


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("watch_stopwords"))
def watch_stopwords(client, message):
    msg_text = '\n'.join(STOPWORDS_RU)
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, msg_text)


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("statistics"))
def get_chat_history(client, message):
    STAT_CHANNEL_CURRENT = (message.text.split())[1]
    general_list = []
    msg_text = ''
    text_on_day = {}
    current_date = 0
    messages = tg_user_bot.get_chat_history(STAT_CHANNEL_CURRENT, 300)
    for message in messages:
        if message.text is not None:
            if current_date != message.date.date():
                current_date = message.date.date()
                text_on_day[current_date] = split_word(message.text)
            else:
                text_on_day[current_date] = text_on_day[current_date] + split_word(message.text)
    for key in reversed(text_on_day.keys()):
        general_list += text_on_day[key]
        counter = Counter(general_list)
        msg_text += str(key) + ' - ' + '; '.join([f'{key}: {value}' for key, value in counter.most_common(5)]) + '\n'
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, msg_text)


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("wordcloud"))
def get_wordcloud(client, message):
    STAT_CHANNEL_CURRENT = (message.text.split())[1]
    text_chat = ''
    for message in tg_user_bot.get_chat_history(STAT_CHANNEL_CURRENT, 300):
        if message.text is not None:
            text_chat = text_chat + ' ' + message.text
    text_chat = ' '.join(split_word(text_chat))
    mask = numpy.array(Image.open(r""))
    wordcloud = WordCloud(width=2000,
                          height=1500,
                          random_state=1,
                          background_color='white',
                          colormap='Set2',
                          collocations=False,
                          mask=mask).generate(text_chat)
    wordcloud.to_file(r"")
    tg_user_bot.send_photo(config.CHANNEL_FOR_STATISTICS,r"")


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("help"))
def help_for_user(client, message):
    msg_text = "Для того, чтобы получить статистику канала, введите в этом чате одну из двух команд:\n" \
               "/statistics {username} - пять самых встречающихся слов по дням за последние 300 постов;\n" \
               "/wordcloud {username} - облако встречающихся слов за последние 300 постов.\n" \
               "После команды введите ID или Username канала.\n" \
               "Например: /statistics test_messag."
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, msg_text)


@tg_user_bot.on_message(filters.chat(config.CHANNEL_FOR_STATISTICS) and filters.command("dict_stop"))
def help_for_user(client, message):
    msg_text = "Для того, чтобы редактировать словарь стоп-слов, введите в этом чате одну из трех команд:\n" \
               "/add_stopwords {word} - добавление в словарь стоп-слова;\n" \
               "/delete_stopwords {word} - удаление из словаря стоп-слова;\n" \
               "/watch_stopwords - просмотр стоп-слов.\n" \
               "После первых двух команд нужно ввести слово.\n" \
               "Например: /add_stopwords РФ."
    tg_user_bot.send_message(config.CHANNEL_FOR_STATISTICS, msg_text)


if __name__ == '__main__':
    print(datetime.today().strftime(f'%H:%M:%S | Telegram Bot launched'))
    tg_user_bot.run()
