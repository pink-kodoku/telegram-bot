import telebot
from telebot import types

from api import API

import requests

bot_token = '5496527835:AAFBv-2ntjJ-QyxAlnO28L4nxinqfFQGk8U'
news_api_key = 'c43cbda256704de28fa1ea0a1a87f75e'

bot_api = API('news-bot.db')
telebot = telebot.TeleBot(bot_token)

commands = '/start - начать\n/about - о боте\n/categories - подписаться на категории\n/subscribes - мои подписки\n/unsubscribe - отписаться от категории\n/help - команды'
hello_msg = 'Присаживайся поудобнее, здесь всегда тебе рады'


@telebot.message_handler(commands=['start'])
def start(req):
    user_id = req.chat.id

    if not bot_api.has_user(user_id):
        bot_api.add_user(user_id)

    telebot.send_message(user_id, f'{hello_msg} \n{commands}')


@telebot.message_handler(commands=['subscribes'])
def get_user_subscribes(req):
    user_id = req.chat.id
    res = ''
    subscribes = bot_api.get_subscribes(user_id)
    markup = types.InlineKeyboardMarkup()

    if bool(len(subscribes)):
        res = 'выберите категорию новостей:\n/unsubscribe - отписаться'
        for subscribe in subscribes:
            markup.add(types.InlineKeyboardButton(subscribe[1], callback_data=f'get_news-{subscribe[1]}'))
    else:
        res = 'вы не подписаны ни на одну категорию\n/categories - подписаться'

    telebot.send_message(user_id, f'{req.from_user.first_name}, ' + res, reply_markup=markup)


@telebot.message_handler(commands=['categories'])
def get_categories(req):
    categories = bot_api.get_categories()
    markup = types.InlineKeyboardMarkup()

    for category in categories:
        markup.add(types.InlineKeyboardButton(category[1], callback_data=f'sub_category-{category[0]}'))

    telebot.send_message(req.chat.id, 'Доступные категории:', reply_markup=markup)


def subscribe_category(user_id, category_id):
    category = bot_api.get_category(category_id)
    res = ''

    if not bot_api.is_subscribed(user_id, category_id):
        bot_api.subscribe_category(user_id, category_id)

        res = f'Вы успешно подписались на категорию {category[1]} \n/subscribes - мои подписки'
    else:
        res = f'Вы уже подписаны на категорию {category[1]} \n/subscribes - мои подписки'

    return res


@telebot.message_handler(commands=['unsubscribe'])
def unsubscribe_category(req):
    subscribes = bot_api.get_subscribes(req.chat.id)

    markup = types.InlineKeyboardMarkup()

    for category in subscribes:
        markup.add(types.InlineKeyboardButton(category[1], callback_data=f'unsub_category-{category[0]}'))

    telebot.send_message(req.chat.id, 'Выберите категорию от которой хотите отписаться:', reply_markup=markup)


def get_news(category_news, chat_id):
    response = requests.get(
        f'https://newsapi.org/v2/top-headlines?category={category_news}&country=ru&apiKey={news_api_key}&pageSize=5')

    for post in response.json()['articles']:
        get_image(chat_id, post['urlToImage'], post['title'])


def get_image(chat_id, image_url, caption):
    send_text = f'https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={chat_id}&parse_mode=HTML&caption={caption}&photo={image_url}'
    res = requests.get(send_text)

    return res.json()


@telebot.message_handler(commands=['help'])
def get_help(req):
    telebot.send_message(req.chat.id, f'Доступные команды: \n{commands}')


@telebot.message_handler(commands=['about'])
def get_info(req):
    telebot.send_message(req.chat.id,
                         f'Доступные команды :\n{commands}')


@telebot.callback_query_handler(func=lambda call: True)
def check_other_commands(call):
    command_name = call.data.split('-')[0]
    data = call.data.split('-')[1]
    user_id = call.message.chat.id
    res = ''

    if command_name == 'sub_category':
        category_id = data

        res = subscribe_category(user_id, category_id)
    elif command_name == 'get_news':
        category_news = data

        get_news(category_news, user_id)

        res = f'Новости по категории: {category_news}\nПодписаться еще на категории \n/categories'
    elif command_name == 'unsub_category':
        category_id = data

        print(bot_api.unsubscribe_category(user_id, category_id))

        res = f'Вы успешно отписались\n/subscribes - мои подписки'

    telebot.send_message(user_id, res)
    # telebot.answer_callback_query(call.id)


telebot.polling(none_stop=True)
