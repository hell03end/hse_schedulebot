__author__ = 'Bogdan'
__email__ = 'evstrat.bg@gmail.com'
__mobile_phone__ = 89252608400

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, RegexHandler
from telegram.ext.dispatcher import run_async
import json
import requests
import logging
import time
import datetime
import re
import threading
from random import randint
import pymysql
from retrying import retry
from config import ALLTESTS, ADMIN_ID, TOKEN, botan_token, MYSQL_CONN


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

furry_answers = ['¯\_(ツ)_/¯', 'https://pp.vk.me/c622121/v622121216/6328c/KbDRxEMyUQY.jpg',
                 'https://pp.vk.me/c629212/v629212216/1a9bf/tKVm58ZuFf8.jpg',
                 'Не спешите, вечер не скоро',
                 'Неплохо, очень неплохо. Правда, ты упустил почти все важное, но тем не менее',
                 'Это нелегко для великого ума — допустить чьё-то превосходство',
                 'История повторяется. Колеса крутятся, но ничего нового',
                 'Я не нравлюсь многим людям лишь потому, что у меня есть своё мнение. А ты?',
                 'Мозговитость теперь сексуальна',
                 'Знание — это обладание. © Чарльз Огастес Магнуссен',
                 'Порой обман столь дерзок, что ты не видишь его, даже если все совершенно очевидно',
                 'Хорошей лжи нужны подробности',
                 'Есть вещи, которые не должны прятаться за стеклом. Им требуется прикосновение',
                 'Поспешные выводы опасны',
                 'С плохими людьми надо по-плохому',
                 'Наши традиции нас определяют',
                 'Hе пытайся развлечь меня беседой, это не твой конёк',
                 'Быть умным — это одно, а умничать — другое']


days_rus = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
days = {'Пн': 'Mon', 'Вт': 'Tue', 'Ср': 'Wed', 'Чт': 'Thu', 'Пт': 'Fri', 'Сб': 'Sat', 'Вс': 'Sun'}


days_to_eng = {'Понедельник': 'Mon', 'Вторник': 'Tue', 'Среда': 'Wed',
                          'Четверг': 'Thu', 'Пятница': 'Fri', 'Суббота': 'Sat'}


custom_keyboard = [['Пары на сегодня', 'Пары на завтра'], ['Пары на неделю'], ['Связаться с админом'],
                   ['Баш', 'Надо ли мне на пары?']]


custom_keyboard_week = [['Понедельник', 'Четверг'], ['Вторник', 'Пятница'],
                        ['Среда', 'Суббота'], ['Назад']]


day_of_week_to_num = {'Mon': 0, 'Tue': 1, 'Wed': 2,
                        'Thu': 3, 'Fri': 4, 'Sat': 5,
                        'Sun': 6}

lessons_number = {'09:00': '1 пара', '10:30': '2 пара', '12:10': '3 пара',
                  '13:40': '4 пара', '15:10': '5 пара', '16:40': '6 пара',
                  '18:10': '7 пара', '19:40': '8 пара',
                  '15:20': '5 пара', '16:50': '6 пара', '14:10': '5 пара', '15:40': '5 пара', '19:00': '8 пара',
                  '08:40': '1 пара', '09:30': '1 пара', '11:10': '2 пара', '12:40': '3 пара', '14:20': '5 пара',
                  '15:50': '6 пара', '10:00': '2 пара', '15:00': '5 пара', '12:00': '3 пара', '10:35': '2 пара',
                  '16:00': '6 пара', '17:10': '6 7 пара', '18:20': '7 пара', '19:50': '8 пара'}


reply_markup_commads = ReplyKeyboardMarkup(custom_keyboard)
reply_markup_commads_week = ReplyKeyboardMarkup(custom_keyboard_week)

TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'

class MYSQL():
    def __init__(self):
        self.connection = pymysql.connect(**MYSQL_CONN)
        self.cursor = self.connection.cursor()


    def create_table_users(self):
        self.table = 'CREATE TABLE users (chat_id INTEGER, EMAIL TEXT)'
        self.cursor.execute(self.table)

    def insert_user(self, chat_id, email):
        query = 'INSERT INTO users (chat_id, EMAIL) VALUES ({}, "{}")'.format(chat_id, email)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def search_lessons_chatid(self, chat_id):
        query = 'SELECT Mon, Tue, Wed, Thu, Fri, Sat, Sun FROM lessons WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def delete_lessons(self, chat_id):
        query = 'DELETE FROM lessons WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def delete_user(self, chat_id):
        query = 'DELETE FROM users WHERE chat_id="{}"'.format(chat_id)
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def search_all(self, table):
        query = 'SELECT * FROM {}'.format(table)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_user_chatid(self, chatid):
        query = 'SELECT * FROM users WHERE chat_id="{}"'.format(chatid)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_schedule(self, column, lesson, chat_id):
        query = 'UPDATE lessons SET {}="{}" WHERE chat_id={}'.format(column, lesson, chat_id)
        self.cursor.execute(query)
        self.connection.commit()

    def lessons_dayofweek(self, day, chat_id):
        query = 'SELECT {} FROM lessons WHERE chat_id="{}"'.format(day, chat_id)
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def close_conn(self):
        self.connection.close()

    def do(self, query):
        self.cursor.execute(query)
        self.connection.commit()


class Botan(object):
    def track(self, token, uid, message, name):
        try:
            r = requests.post(
                TRACK_URL,
                params={"token": token, "uid": uid, "name": name},
                data=json.dumps(message),
                headers={'Content-type': 'application/json'},
            )
            return json.loads(r.text)
        except requests.exceptions.Timeout:
            # set up for a retry, or continue in a retry loop
            return False
        except (requests.exceptions.RequestException, ValueError) as e:
            # catastrophic error
            print(e)
            return False


    def shorten_url(self, url, botan_token, user_id):
        """
        Shorten URL for specified user of a bot
        """
        try:
            return requests.get(SHORTENER_URL, params={
                'token': botan_token,
                'url': url,
                'user_ids': str(user_id),
            }).text
        except:
            return url


botan = Botan()
last_chat_id = 0
last_user_start = set()


def day_define():
    t = time.ctime()
    date = str(datetime.datetime.now())[:10].split('-')
    day_of_the_week = t[:3]
    return (date, day_of_the_week)


def addition_days(n):
    addition_days = str(datetime.datetime.now() + datetime.timedelta(days=n))[:10]
    return addition_days.replace('-', '.')


def subtract_days(n):
    subtract_days = str(datetime.datetime.now() - datetime.timedelta(days=n))[:10]
    return subtract_days.replace('-', '.')


def parsing_lessons(schedule, upd_type='week'):
    d = json.loads(schedule)
    if d['StatusCode']['Description'] == 'OK':
        lessons = []
        for day in days_rus:
            schedule_lessons = ''
            if d['Lessons'] is None:
                continue
            for lesson in d['Lessons']:
                if lesson['dayOfWeekString'] == day:
                    if lesson['beginLesson'] in lessons_number:
                        schedule_lessons += lessons_number[lesson['beginLesson']] + '\r\n' + lesson['kindOfWork'] + '\r\n' + lesson['lecturer'] + '\r\n' + lesson['discipline'] + '\r\n' + \
                                lesson['auditorium'] + '\r\n' + lesson['beginLesson'] + '-' + lesson['endLesson'] + '\r\n' + \
                                lesson['building'] + '\r\n~~~~~~~~~~~~~\r\n'
                    else:
                        schedule_lessons += lesson['kindOfWork'] + '\r\n' + lesson['lecturer'] + '\r\n' + lesson['discipline'] + '\r\n' + \
                                 lesson['auditorium'] + '\r\n' + lesson['beginLesson'] + '-' + lesson['endLesson'] + '\r\n' + \
                                 lesson['building'] + '\r\n~~~~~~~~~~~~~\r\n'
            schedule_lessons = re.sub('[\\\\"]', '', schedule_lessons)
            if upd_type == 'week':
                if schedule_lessons == '':
                    lessons.append((day, 'Нет пар'))
                    continue
                else:
                    lessons.append((day, schedule_lessons.replace('\\', '')))

        return lessons
    return d['StatusCode']['Description']


@retry(stop_max_attempt_number=3)
def add_lessons(email, from_date, to_date, from_id):
    url = 'http://92.242.58.221/ruzservice.svc/v2/personlessons?fromdate={}&todate={}&email={}'.format(from_date,
                                                                                                       to_date,
                                                                                                       email)
    print(url)
    schedule = requests.get(url).content.decode('utf8')
    if schedule:
        lessons = parsing_lessons(schedule)
        if not isinstance(lessons, str):
            columns = ', '.join([days[d[0]] for d in lessons])
            rows = ', '.join(['"{}"'.format(l[1]) for l in lessons])
            q = 'insert into lessons (chat_id, {}) values ({}, {})'.format(columns, from_id, rows)
            mysql = MYSQL()
            mysql.do(q)
            mysql.close_conn()
            print('Скачал пары для ' + email)
            return True
        return lessons
    else:
        return False


@retry(stop_max_attempt_number=3)
def start(bot, update):
    print(update)
    print('\n')
    chat_id = update.message.chat_id
    from_id = update.message.from_user.id

    mysql = MYSQL()
    email = mysql.search_user_chatid(from_id)
    if email != ():
        url = 'http://92.242.58.221/ruzservice.svc/v2/' \
              'personlessons?fromdate={}&todate={}&email={}'.format(addition_days(0), addition_days(6), email[0][2])
        page = requests.get(url).content.decode('utf8')
        html = parsing_lessons(page)
        if html is not False:
            for day, schedule in html:
                mysql = MYSQL()
                mysql.update_schedule(days[day], schedule, from_id)
        print('Проапдейтил {}'.format(from_id))
        bot.sendMessage(chat_id, 'Хей, я тебя помню!\r\nВот клавиатура команд\r\nНо если ты хочешь поменять '
                                 'email, то отправь мне /delete', reply_markup=reply_markup_commads)
    else:
        bot.sendMessage(chat_id, text='Для начала мне нужно знать твою группу. Для этого вспомни и введи '
                                  'свою корпоративную почту :) Она заканчивается на @edu.hse.ru и '
                                  'используется для входа в LMS\r\nЕсли ты отправляешь сообщение из '
                                  'группового чата, то добавь "/" в начало почты, иначе я ее не увижу')
        last_user_start.add(from_id)
    mysql.close_conn()


@run_async
def new_user(bot, update):
    chat_id = update.message.chat_id
    message = update.message.text.replace('/', '')
    from_id = update.message.from_user.id

    print(update)
    print(message)
    print('\n')

    if from_id in last_user_start:
        last_user_start.discard(from_id)
        mysql = MYSQL()
        if mysql.search_user_chatid(from_id) == ():
            bot.sendMessage(chat_id, 'Пробую скачать твое расписание')
            res = add_lessons(message, addition_days(0), addition_days(6), from_id)
            if not isinstance(res, str):
                mysql.insert_user(from_id, message.lower())
                bot.sendMessage(chat_id, 'Вот тебе клавиатура команд. Используй её с умом 😉', reply_markup=reply_markup_commads, parse_mode=ParseMode.HTML)
            else:
                bot.sendMessage(chat_id, 'Я попытался найти твои пары, но система мне вернула \n <b>{}</b>'.format(res), parse_mode=ParseMode.HTML)
        else:
            bot.sendMessage(chat_id, 'Так ты уже уже тут! Хочешь двойную порцию пар?)')
        mysql.close_conn()
    else:
        pass



@run_async
def lessons_today(bot, update):
    chat_id = update.message.chat_id
    from_id = update.message.from_user.id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    botan.track(botan_token, chat_id, message_dict, 'lessons_today')

    mysql = MYSQL()
    lesson = mysql.lessons_dayofweek(day_define()[1], from_id)
    if lesson:
        lessons = lesson[0]
        if day_define()[1] == 'Sun':
            photo = 'https://pp.vk.me/c628429/v628429216/4a2d6/ICkqFNVA6dE.jpg'
            bot.sendPhoto(chat_id, photo=photo, reply_markup=reply_markup_commads)
        else:
            bot.sendMessage(chat_id, lessons, reply_markup=reply_markup_commads, parse_mode=ParseMode.HTML)
    else:
        bot.sendMessage(chat_id, 'Тебя нет в базе, отправь /start', reply_markup=reply_markup_commads)
    mysql.close_conn()


@run_async
def lessons_tmrw(bot, update):
    chat_id = update.message.chat_id
    from_id = update.message.from_user.id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    botan.track(botan_token, chat_id, message_dict, 'lessons_tmrw')

    mysql = MYSQL()
    lesson = mysql.search_lessons_chatid(from_id)
    if lesson:
        lesson = lesson[0]
        next_day = day_of_week_to_num[day_define()[1]] + 1
        if next_day == 6:
            photo = 'https://pp.vk.me/c628429/v628429216/4a2d6/ICkqFNVA6dE.jpg'
            bot.sendPhoto(chat_id, photo=photo, reply_markup=reply_markup_commads)
        elif next_day == 7:
            bot.sendMessage(chat_id, lesson[0], reply_markup=reply_markup_commads, parse_mode=ParseMode.HTML)
        else:
            bot.sendMessage(chat_id, lesson[next_day], reply_markup=reply_markup_commads, parse_mode=ParseMode.HTML)
    else:
        bot.sendMessage(chat_id, 'Тебя нет в базе, отправь /start', reply_markup=reply_markup_commads)
    mysql.close_conn()


def delete_user(bot, update):
    chat_id = update.message.chat_id
    from_id = update.message.from_user.id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    event_name = update.message.text
    botan.track(botan_token, chat_id, message_dict, event_name)

    mysql = MYSQL()
    if mysql.search_user_chatid(from_id):
        mysql.delete_user(from_id)
        mysql.delete_lessons(from_id)
        bot.sendPhoto(from_id, photo=open('/home/vmuser/hseshedule_bot/gg.jpeg', 'rb'))
        mysql.close_conn()
    else:
        bot.sendMessage(chat_id, 'Нужно добавиться, чтобы удалятся, логично?')


def admin_contacts(bot, update):
    chat_id = update.message.chat_id

    print(update)
    print('\n')
    message_dict = update.message.to_dict()
    event_name = update.message.text
    botan.track(botan_token, chat_id, message_dict, 'admin_contacts')

    bot.sendMessage(chat_id, 'Вопросы/пожелания/предложения/благодарности/ненависти/чтонибудьеще '
                             'можно писать @Evstrat :)', reply_markup=reply_markup_commads)


def week_days_choice(bot, update):
    chat_id = update.message.chat_id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    botan.track(botan_token, chat_id, message_dict, 'choose_week_days')

    bot.sendMessage(chat_id, 'Выбери день недели', reply_markup=reply_markup_commads_week)


def lessons_week(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text
    from_id = update.message.from_user.id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    event_name = update.message.text
    botan.track(botan_token, chat_id, message_dict, days_to_eng[text])

    mysql = MYSQL()
    msg = mysql.lessons_dayofweek(days_to_eng[text], from_id)
    bot.sendMessage(chat_id, msg[0], reply_markup=reply_markup_commads_week)
    mysql.close_conn()


def return_keyboard(bot, update):
    chat_id = update.message.chat_id

    print(update)
    print('\n')

    bot.sendMessage(chat_id, 'Вот предыдущее меню', reply_markup=reply_markup_commads)


def random_answer(bot, update):
    chat_id = update.message.chat_id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    botan.track(botan_token, chat_id, message_dict, 'random_answer')

    msg = furry_answers[randint(0, len(furry_answers)-1)]
    if msg.startswith('https'):
        bot.sendPhoto(chat_id, photo=msg)
    else:
        bot.sendMessage(chat_id, msg, reply_markup=reply_markup_commads, parse_mode=ParseMode.HTML)


bash_arr = []
def fill_bash_arr():
    url = 'http://bash.im/best'
    page = requests.get(url).content.decode('1251')
    text = re.findall('<div class="text">(.*?)</div>', page, flags=re.DOTALL)
    for t in text:
        bash_arr.append(t.replace('<br>', '\n').replace('&quot', '\"').replace('&gt', '>').replace(';', ''))


def bash_quote(bot, update):
    chat_id = update.message.chat_id
    message_dict = update.message.to_dict()
    botan.track(botan_token, chat_id, message_dict, 'bash')

    if len(bash_arr) == 0:
        fill_bash_arr()
    else:
        msg = bash_arr[randint(0, len(bash_arr)-1)]
        bot.sendMessage(chat_id, msg)


def nvmnd(bot, update):
    chat_id = update.message.chat_id

    print(update)
    print('\n')

    message_dict = update.message.to_dict()
    event_name = update.message.text
    botan.track(botan_token, chat_id, message_dict, 'ty')

    bot.sendMessage(chat_id, 'Не за что :)', reply_markup=reply_markup_commads)


def help(bot, update):
    print(update)
    print('\n')
    bot.sendMessage(update.message.chat_id, text='Чтобы узнавать пары, отправь /start или напиши администратору @Evstrat. Это живой человек :)')


def unknown_command(bot, update):
    print(update)
    print('\n')
    bot.sendMessage(update.message.chat_id, text='Ничего не понимаю. Такой команды нет')



def sendtoall(bot, update):
    from_id = update.message.from_user.id
    if from_id == ADMIN_ID:
        print('Начинаю отправлять')
        mysql = MYSQL()
        for _id, chat_id, email, dt in mysql.search_all('users'):
            try:
                bot.sendMessage(chat_id, 'Если вы пишете на python3, можете мне рассказать что-то о работе с базами данных, то пишите мне, '
                                         '@Evstrat, пообщаемся :)')
            except:
                continue
        mysql.close_conn()
        print('Всем отправил')


def cancel(bot, update):
    if update.message.from_user.id == ADMIN_ID:
        sendtoall_set.clear()
        bot.sendMessage(ADMIN_ID, 'Отменил')


def pong(bot, update):
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id, 'pong')


def need_update():
    while True:
        now_time = str(datetime.datetime.now())[11:16]
        if now_time == '21:00':
            bash_arr.clear()
            fill_bash_arr()
            time.sleep(60)


print('Бот запущен')
updater = Updater(TOKEN, workers=10)

dp = updater.dispatcher

# COMMANDS
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help))
dp.add_handler(CommandHandler('ok', help))
dp.add_handler(CommandHandler('delete', delete_user))
dp.add_handler(CommandHandler('delete@hseschedule_bot', delete_user))


dp.add_handler(CommandHandler('cancel', cancel))
dp.add_handler(CommandHandler('sendmessages', sendtoall))


# Regex handlers will receive all updates on which their regex matches
dp.add_handler(RegexHandler('Пары на сегодня', lessons_today))
dp.add_handler(RegexHandler('Пары на завтра', lessons_tmrw))
dp.add_handler(RegexHandler('Связаться с админом', admin_contacts))
dp.add_handler(RegexHandler('Пары на неделю', week_days_choice))
dp.add_handler(RegexHandler('Надо ли мне на пары?', random_answer))
dp.add_handler(RegexHandler('.пасиб.*', nvmnd))
dp.add_handler(RegexHandler('Назад', return_keyboard))
dp.add_handler(RegexHandler('Баш', bash_quote))
dp.add_handler(RegexHandler('[pP]ing', pong))
dp.add_handler(RegexHandler('[ПВСЧ][отреяу][ноетб][ердвнб][днаеио][еирцт]?[лкга]?(ьник)?', lessons_week))


# String handlers work pretty much the same
# dp.addStringCommandHandler('reply', cli_reply)

dp.add_handler(RegexHandler('.*@edu.hse.ru', new_user))

# All TelegramErrors are caught for you and delivered to the error
# handler(s). Other types of Errors are not caught.

# Start the Bot and store the update Queue, so we can insert updates
update_queue = updater.start_polling()


upd_need = threading.Thread(target=need_update)

upd_need.start()
