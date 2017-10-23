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
    return map(lambda user: (user.email, user.student), Users)


def fetch_schedule(email: str, api: object=api, is_student: bool=True) -> list:
    """ download schedule for each email """
    if is_student:
        return api.schedule(email)
    return api.schedule(email, receiverType=1)


def format_lessons(lessons: Collection, schema: dict=MESSAGE_SCHEMA,
                   city: str="moscow", **kwargs) -> Generator:
    """ apply correct message schema to lesson """
    for lesson in lessons:
        lesson_time = LESSONS_TIMETABLE[city].get(lesson.get('beginLesson'))
        time_message = MESSAGES['format_lesson:time'].format(lesson_time)
        if not lesson_time:
            time_message = f"{lesson.get('beginLesson')} - " \
                           f"{lesson.get('endLesson')}"
        yield schema.format(
            time=time_message,
            name=lesson.get('discipline', "Undefined"),
            type=lesson.get('kindOfWork', "Undefined"),
            teacher=lesson.get('lecturer', "Professor"),
            place=lesson.get('building', "Moscow, HSE"),
            room=lesson.get('auditorium', "???")
        )


def format_day_schedule(lessons: Iterable, schema: dict=POST_SCHEMA,
                        **kwargs) -> str:
    """ apply correct day schema to list of this day lessons """
    return schema.format(
        date=f"{DAYS[lessons[0].get('dayOfWeek', 0)]}, "
             f"{lessons[0].get('date', '...')}",
        messages="\n\n".join(lesson for lesson in format_lessons(lessons,
                                                                 **kwargs))
    )


def format_schedule(schedule: Collection, **kwargs) -> list:
    """ apply schema for all days with lessons in schedule """
    days = [[] for _ in range(7)]
    for lesson in schedule:
        days[lesson['dayOfWeek'] - 1].append(lesson)
    lessons = [[] for _ in range(7)]
    for idx, day in enumerate(days):
        if day:
            lessons[idx] = format_day_schedule(day, **kwargs)
        else:
            lessons[idx] = MESSAGES['format_schedule:empty']
    return lessons


def update_schedules(schedules: (list, tuple), email: str) -> None:
    """ format and save (update) schedules to database """
    student = Users.get(email=email)
    lessons_obj, _ = Lessons.get_or_create(student=student)
    schedule = format_schedule(schedules)

    lessons = dict(zip(TABLE_MAPPING, schedule))
    Lessons.update(**lessons).where(Lessons.id == lessons_obj.id).execute()


def get_and_save(email: Iterable) -> None:
    """ pipeline for getting and saving schedules """
    update_schedules(fetch_schedule(email[0], is_student=email[1]), email[0])


def main() -> None:
    pool = Pool(5)
    pool.map(get_and_save, get_emails(), chunksize=35)
