""" Collection of bot messages """

from emoji import emojize


MESSAGES = {
    'service:mailing': {
        'do_mailing:end': "Разослал. Сообщение получили {}.",
        'whom_to_send:ask': "Кому будем рассылать?",
        'whom_to_send:spam': "...",
        'recipients:ask': "Напиши, что будем отправлять.",
        'recipients:back': "Вот предыдущее меню.",
        'prepare_mailing:start': "Начал рассылку. "
                                 "Я напишу тебе, когда закончу.",
        'prepare_mailing:empty': "Некому отправлять :(",
    },
    'service:common_handlers': {
        'start:greetings':
            "Привет, как дела?",
        'start:greetings_new': "Привет! У меня можно подсмотреть расписание "
            "пар (в том числе, преподавателям) "
            "{}".format(emojize(':winking_face:')),
        'ask_email:ask': "Введи твой корпоративный адрес электронной почты. "
                         "Да-да, тот который на hse.ru заканчивается",
        'ask_city:ask': "В вышке какого города учитесь/преподаете?",
        'show_about': "Я умею показывать расписание занятий как для "
            "студентов, так и для преподавателей. Скоро я научусь и "
            "другим полезным функциям",
        'cancel': "Начнем с начала",
        'get_email:incorrect': "А ты точно из Вышки? А то email не подходит "
            ":(",
        'get_email:correct': "Почту запомнил!",
        'get_city:incorrect': "К сожалению, в этом городе еще нет НИУ ВШЭ, "
            "переезжаем в Москву... (можно изменить в настройках)",
        'get_city:msg': "Город запомнил.",
        'add_user:msg': "Ну, будем дружить? " + emojize(':smiling_face:')
    },
    'utils:functions': {
        'check_back:msg': "Вот предыдущее меню"
    },
    'schedule:week': {
        'on_week:ask': "Выбери день недели {}".format(
            emojize(':tear-off_calendar:')),
        'choose_dow:empty': "Нет пар",
        'choose_dow:back': "Вот предыдущее меню.",
        'choose_dow:ask': "Выбери вариант на клавиатуре",
        'choose_dow:cancel': "Начнем с начала",
        'choose_dow:spam': "День недели не найден"
    },
    'service:settings': {
        'on_settings:unregistered': "Сначала надо зарегистрироваться!",
        'current': "Текущие настройки:\nEmail: {}\nГород: {}",
        'choose_menu:spam': "Извините, я вас не понял :(",
        'choose_menu:feedback': "Свой отзыв/предложение/вопрос пиши в: "
            "https://t.me/joinchat/A2Ahbgvbg3mq2b_WnDvWVw",
        'on_back:msg': "Вот предыдущее меню",
        'choose_menu:ask_email': "Введи новый адрес корпоративной почты:",
        'choose_menu:ask_city': "Введи свой город:",
        'get_email:back': "Отмена...",
        'get_email:incorrect': "А ты точно их Вышки? А то email не подходит "
            ":(",
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
        'on_spam': "Ой."
    }
}
