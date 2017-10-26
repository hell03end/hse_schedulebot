""" Collection of custom keyboards used in bot """

START_KEYBOARD = [
    ['Расписание'],
    ['Настройки']
]

BACK_KEY = ['Назад']

REGISTER_KEYBOARD = [
    ['Зарегистрироваться'],
    ['Информация']
]

CITIES_KEYBOARD = [
    ['Москва', 'Москва:Дубки'],
    ['Санкт-Петербург'],
    ['Пермь'],
    ['Нижний Новгород']
]

CITIES_KEYBOARD_BACK = CITIES_KEYBOARD.copy()
CITIES_KEYBOARD_BACK.append(BACK_KEY)

SETTINGS_KEYBOARD = [
    ['О боте'],
    ['Email', 'Город'],
    # ['Добавить Электрички'],
    ['Написать разработчикам']
]
SETTINGS_KEYBOARD.append(BACK_KEY)

SCHEDULE_KEYBOARD = [
    ['На сегодня', 'На завтра'],
    ['На неделю']
]
SCHEDULE_KEYBOARD.append(BACK_KEY)

WEEK_KEYBOARD = [
    ['Понедельник', 'Четверг'],
    ['Вторник', 'Пятница'],
    ['Среда', 'Суббота']
]
WEEK_KEYBOARD.append(BACK_KEY)

MAILING_WHOM_KEYBOARD = [
    ['Всем'],
    ['Студентам', 'Преподавателям']
]
MAILING_WHOM_KEYBOARD.append(BACK_KEY)

SCHEDULE_KEYBOARD_STUDENT = SCHEDULE_KEYBOARD.copy()
SCHEDULE_KEYBOARD_STUDENT.insert(0, ['Найти преподавателя'])

START_KEYBOARD_STUDENT = START_KEYBOARD
START_KEYBOARD_STUDENT_TRAINS = START_KEYBOARD.copy()
START_KEYBOARD_STUDENT_TRAINS.insert(1, ['Электрички'])
