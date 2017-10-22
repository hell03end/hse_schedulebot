START_KEYBOARD = [
    ['Расписание'],
    ['Настройки']
]

BACK_KEY = ['Назад']

SETTINGS_KEYBOARD = [
    ['О боте'],
    ['Изменить email'],
    ['Изменить город'],
    # ['Добавить Электрички'],
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

WEEK_KEYBOARD_STUDENT = WEEK_KEYBOARD.copy().insert(0, ['Найти преподователя'])

START_KEYBOARD_STUDENT = START_KEYBOARD
START_KEYBOARD_STUDENT_TRAINS = START_KEYBOARD.copy().insert(1, ['Электрички'])
