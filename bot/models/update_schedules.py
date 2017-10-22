from collections import Collection, Generator, Iterable
from multiprocessing import Pool

from ruz import RUZ

from bot.models.models import Lessons, Users
from bot.utils.messages import MESSAGES
from bot.utils.schema import (DAYS, LESSONS_TIMETABLE, MESSAGE_SCHEMA,
                              POST_SCHEMA, TABLE_MAPPING)

MESSAGES = MESSAGES['models:update_schedules']
api = RUZ()


def get_emails() -> Generator:
    """ return emails from Users database """
    return map(lambda user: user.email, Users)


def fetch_schedule(email: str, api: object=api, **kwargs) -> list:
    """ download schedule for each email """
    return api.schedule(email, **kwargs)


def format_lessons(lessons: Collection,
                   schema: dict=MESSAGE_SCHEMA) -> Generator:
    """ apply correct message schema to lesson """
    for lesson in lessons:
        lesson_time = LESSONS_TIMETABLE.get(
            lesson.get('beginLesson'),
            f"{lesson.get('beginLesson')} - {lesson.get('endLesson')}"
        )
        yield schema.format(
            time=MESSAGES['format_lesson:time'].format(lesson_time),
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
        lessons[idx] = format_day_schedule(day) if day else None
    return lessons


def update_schedules(schedules: (list, tuple), email: str) -> None:
    """ format and save (update) schedules to database """
    student = Users.get(email=email)
    lessons_obj, _ = Lessons.get_or_create(student=student)
    if not schedules:
        lessons_obj.delete_instance()
        return
    schedule = format_schedule(schedules)

    lessons = dict(zip(TABLE_MAPPING, schedule))
    Lessons.update(**lessons).where(Lessons.id == lessons_obj.id).execute()


def get_and_save(email: str) -> None:
    """ pipeline for getting and saving schedules """
    update_schedules(fetch_schedule(email), email)


def main() -> None:
    pool = Pool(5)
    pool.map(get_and_save, get_emails(), chunksize=35)
