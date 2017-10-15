from collections import Collection, Generator, Iterable
from datetime import datetime
from multiprocessing import Pool

from models import Lessons, Users
from ruz import RUZ

from utils.schema import MESSAGE_SCHEMA, POST_SCHEMA

DAYS = {
    0: "Undefined",
    1: "Пн",
    2: "Вт",
    3: "Ср",
    4: "Чт",
    5: "Пт",
    6: "Сб",
    7: "Вс"
}

LESSONS_NUMBER = {
    '09:00': "1", '08:40': "1", '09:30': "1",
    '10:30': "2", '11:10': "2", '10:00': "2", '10:35': "2",
    '12:10': "3", '12:40': "3", '12:00': "3",
    '13:40': "4",
    '15:10': "5", '14:10': "5", '15:40': "5", '15:20': "5", '14:20': "5", '15:00': "5",
    '16:40': "6", '16:50': "6", '16:00': "6", '15:50': "6",
    '17:10': "6 7",
    '18:10': "7", '18:20': "7",
    '19:40': "8", '19:00': "8", '19:50': "8"
}


api = RUZ(strict_v1=True)


def get_emails() -> Generator:
    """ return emails from Users database """
    return map(lambda user: user.email, Users)


def fetch_schedules(emails: Collection,
                    api: object=api,
                    **kwargs) -> Generator:
    """ download schedule for each email """
    return map(lambda email: api.schedule(email, **kwargs), emails)


def format_lessons(lessons: Collection,
                   schema: dict=MESSAGE_SCHEMA) -> Generator:
    """ apply correct message schema to lesson """
    for lesson in lessons:
        lesson_time = LESSONS_NUMBER.get(
            lesson.get('beginLesson'),
            f"{lesson.get('beginLesson')} - {lesson.get('endLesson')}"
        )
        yield schema.format(
            time=f"{lesson_time} пара",
            name=lesson.get('discipline', "Undefined"),
            type=lesson.get('kindOfWork', "Undefined"),
            teacher=lesson.get('lecturer', "Professor"),
            place=lesson.get('building', "Moscow, HSE"),
            room=lesson.get('auditorium', "???")
        )


def format_day_schedule(lessons: Iterable,
                        schema: dict=POST_SCHEMA) -> str:
    """ apply correct day schema to list of this day lessons """
    return schema.format(
        date=f"{DAYS[lessons[0].get('dayOfWeek', 0)]},"
             f"{lessons[0].get('date', '...')}",
        messages="\n\n".join(lesson for lesson in format_lessons(lessons))
    )


def format_schedule(schedule: Collection) -> list:
    """ apply schema for all days with lessons in schedule """
    days = [[] for _ in range(7)]
    for lesson in schedule:
        days[lesson['dayOfWeek'] - 1].append(lesson)
    lessons = [[] for _ in range(7)]
    for idx, day in enumerate(days):
        lessons[idx] = format_day_schedule(day) if day else ""
    return lessons


def update_schedules(schedules: (list, tuple), email: str) -> None:
    """ format and save (update) schedules to database """
    for schedule in schedules:
        if not schedule:
            continue
        schedule = format_schedule(schedule)
        student = Users.get(email=email)
        lesson = Lessons.get_or_create(student=student)

        lesson.monday = schedule[0]
        lesson.tuesday = schedule[1]
        lesson.wednesday = schedule[2]
        lesson.thursday = schedule[3]
        lesson.friday = schedule[4]
        lesson.saturday = schedule[5]
        lesson.sunday = schedule[6]
        lesson.upd_dt = datetime.now()
        lesson.save()


def get_and_save(emails: Collection or str) -> None:
    """ pipeline for getting and saving schedules """
    if isinstance(emails, str):
        emails = [emails]
    update_schedules(fetch_schedules(emails), emails)


if __name__ == '__main__':
    pool = Pool(1)
    pool.map(get_and_save, get_emails(), chunksize=15)
