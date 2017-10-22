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
        'start:greetings': "Привет! У меня можно подсмотреть расписание "
                           "твоей учебы {}".format(emojize(':winking_face:'))
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
        'on_back:msg': "Вот предыдущее меню."
    }
}

# regexpr triggers
TRIGGERS = {}
