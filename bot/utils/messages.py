""" Collection of bot messages """

import re
from random import randint

from emoji import emojize


def on_spam_day(message: str=None) -> str:
    sunday_m = ("Никто не учится по воскресеньям.",
                "Когда-то же нужно отдыхать.",
                "Предлогаю перерыв?",
                "'Сделай паузу, скушай твикс!'")
    weekday_m = ("В моем календаре нет такого дня.",
                 "День китайской пасхи?",
                 "...",
                 "Ой.")

    if message and re.match(r".*воскр.*", message.lower()):
        return sunday_m[randint(0, len(sunday_m) - 1)]
    return weekday_m[randint(0, len(weekday_m) - 1)]


def on_spam_mailing(message: str=None) -> str:
    how_are_m = ("Все нормально.",
                 "Привет.",
                 "Могло быть и лучше.",
                 "Могло быть и хуже.",
                 "А Вам как кажется?",
                 "Вы как?",
                 ":)")
    spam_m = ("Вроде бы админ, а ведешь себя как ребенок...",
              "...",
              "Не знаю, что и сказать.",
              "WubbaLubbaDubDub!",
              "Все нормально?")

    if message and re.match(r".*(как.?дела|как ты).*", message.lower()):
        return how_are_m[randint(0, len(how_are_m) - 1)]
    return spam_m[randint(0, len(spam_m) - 1)]


def on_spam(message: str=None) -> str:
    how_are_m = ("Все нормально.",
                 "Привет.",
                 "Могло быть и лучше.",
                 "Могло быть и хуже.",
                 "А Вам как кажется?",
                 "Вы как?",
                 ":)")
    abuse_m = (":(",
               "Обидно.",
               "...",
               "Бывает",
               "Ой.")
    spam_m = ("Извините, я Вас не понял.",
              "Этого я не умею :(",
              "...",
              "Не знаю, что и сказать.",
              "Все нормально?",
              "Бывает",
              "Ой.")

    if message and re.match(r".*(как.?дела|как ты).*", message.lower()):
        return how_are_m[randint(0, len(how_are_m) - 1)]
    elif message and re.match(r".*(питух|дура.*|туп.*|глуп.*)",
                              message.lower()):
        return abuse_m[randint(0, len(abuse_m) - 1)]
    return spam_m[randint(0, len(spam_m) - 1)]


MESSAGES = {
    'service:mailing': {
        'do_mailing:end': "Разослал. Сообщение получили {}.",
        'whom_to_send:ask': "Кому будем рассылать?",
        'whom_to_send:spam': on_spam_mailing,
        'recipients:ask': "Напиши, что будем отправлять.",
        'recipients:back': "Вот предыдущее меню.",
        'prepare_mailing:start': "Начал рассылку. "
                                 "Я напишу тебе, когда закончу.",
        'prepare_mailing:empty': "Некому отправлять :(",
    },
    'service:common_handlers': {
        'start:greetings':
            "Привет, как дела?",
        'start:greetings_new': f"Привет! У меня можно подсмотреть расписание "
            f"пар (в том числе преподавателям) {emojize(':winking_face:')}",
        'ask_email:ask': "Введи твой корпоративный адрес электронной почты. "
                         "Да-да, тот который на hse.ru заканчивается",
        'ask_city:ask': "В вышке какого города учитесь/преподаете?",
        'show_about': "Я умею показывать рассписание занятий как для "
            "студентов, так и для преподавателей. В будущем, я научусь и "
            "другим полезным функциям.",
        'cancel': "Начнем с начала.",
        'get_email:incorrect': "А ты точно их Вышки? А то email не подходит :(",
        'get_email:correct': "Почту запомнил!",
        'get_city:incorrect': "К сожалению, в этом городе еще нет НИУ ВШЭ, "
            "переезжаем в Москву... (можно изменить в настройках)",
        'get_city:msg': "Город запомнил.",
        'add_user:msg': f"Ну, будем дружить? {emojize(':smiling_face:')}"
    },
    'schedule:week': {
        'on_week:ask': f"Выбери день недели {emojize(':tear-off_calendar:')}",
        'choose_dow:empty': "Нет пар",
        'choose_dow:back': "Вот предыдущее меню.",
        'choose_dow:ask': "Выбери вариант на клавиатуре",
        'choose_dow:cancel': "Начнем с начала",
        'choose_dow:spam': on_spam_day
    },
    'service:settings': {
        'on_settings:unregistered': "Сначала надо зарегистрироваться!",
        'current': "Текущие настройки:\nEmail: {}\nГород: {}",
        'choose_menu:spam': on_spam,
        'choose_menu:feedback': "Свой отзыв/предложение/вопрос пиши в: "
            "https://t.me/joinchat/A2Ahbgvbg3mq2b_WnDvWVw",
        'on_back:msg': "Вот предыдущее меню",
        'choose_menu:ask_email': "Введи новый адрес корпоративной почты:",
        'choose_menu:ask_city': "Введи свой город:",
        'get_email:back': "Отмена...",
        'get_email:incorrect': "А ты точно их Вышки? А то email не подходит :(",
        'get_email:correct': "Адрес электронной почты успешно изменен",
        'get_city:back': "Отмена...",
        'get_city:incorrect': "В указанном городе нет вышки (как так-то)",
        'get_city:correct': "Город успешно изменен",
        'show_about': "Я умею показывать рассписание занятий как для "
            "студентов, так и для преподавателей. В будущем, я научусь и "
            "другим полезным функциям."
    },
    'schedule:day': {
        'on_day:back': "Вот предыдущее меню",
        'on_day:empty': "Нет пар",
        'on_day:sunday': "Воскресенье, отдыхай :)",
        'on_back:msg': "Вот предыдущее меню"
    },
    'models:update_schedules': {
        'format_lesson:time': "{} пара",
        'format_schedule:empty': "Нет пар"
    },
    'schedule:start': {
        'on_schedule:ask': "На какой день показывать?",
        'on_back:msg': "Вот предыдущее меню",
        'choose_menu:back': "Вот предыдущее меню",
        'on_spam': on_spam
    }
}

# regexpr triggers
TRIGGERS = {
    'info': r"(инфо|о боте|функции)",
    'all': r".*"
}
