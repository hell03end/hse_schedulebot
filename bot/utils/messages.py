""" Collection of bot messages """

from emoji import emojize


MESSAGES = {
    'service:mailing': {
        'do_mailing:end': "Разослал. Сообщение получили {}.",
        'whom_to_send:ask': "Кому будем рассылать?",
        'recipients:ask': "Напиши, что будем отправлять.",
        'prepare_mailing:start': "Начал рассылку. "
                                 "Я напишу тебе, когда закончу.",
        'prepare_mailing:empty': "Некому отправлять :(",
    },
    'service:common_handlers': {
        'start:greetings':
            "Привет! Я Вас помню {}.",
        'start:greetings_new': "Привет! У меня можно подсмотреть расписание "
            "пар (в том числе, преподователям) "
            "{}".format(emojize(':winking_face:')),
        'ask_email:ask': "Введите Ваш корпоративный адрес электронной почты.",
        'ask_city:ask': "В вышке какого города Вы учитесь/преподаете?",
        'show_about': "Я умею показывать рассписание занятий как для "
            "студентов, так и для преподавателей. В будущем, я научусь и "
            "другим полезным функциям.",
        'cancel': "Начнем с начала.",
        'get_email:incorrect': "Введеный email не является вышкинским :( ",
        'get_email:correct': "Вашу почту запомнил!",
        'get_city:incorrect': "К сожалению, в Вашем городе еще нет НИУ ВШЭ, "
            "переезжаем в Москву.",
        'get_city:msg': "Город запомнил.",
        'add_user:msg': "Готов к использованию!"
    },
    'schedule:week': {
        'on_week:ask': "Выбери день недели {}".format(
            emojize(':tear-off_calendar:')),
        'choose_dow:back': "Вот предыдущее меню.",
        'choose_dow:ask': "Выбери вариант на клавиатуре.",
        'choose_dow:cancel': "Начнем с начала."
    },
    'schedule:day': {
        'on_day:back': "Вот предыдущее меню.",
        'on_day:sunday': "Воскресенье, отдыхай :)",
        'on_back:msg': "Вот предыдущее меню."
    },
    'models:update_schedules': {
        'format_lesson:time': "{} пара.",
        'format_schedule:empty': "Нет пар."
    },
    'schedule:start': {
        'on_schedule:ask': "На какой день показывать?",
        'on_back:msg': "Вот предыдущее меню.",
        'choose_menu:back': "Вот предыдущее меню."
    }
}

# regexpr triggers
TRIGGERS = {
    'info': r"(инфо|о боте|функции)"
}
