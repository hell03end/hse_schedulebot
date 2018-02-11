import time
from datetime import datetime
from multiprocessing import Pool
from typing import Generator, Iterable

import ruz

from bot.models.models import Lessons, Users
from bot.utils.messages import MESSAGES
from bot.utils.schema import (DAYS, LESSONS_TIMETABLE, MESSAGE_SCHEMA,
                              POST_SCHEMA, TABLE_MAPPING)
from config import WORKERS_COUNT

MESSAGES = MESSAGES['models:update_schedules']


def get_users() -> Generator:
    """ return email, telegram_id from Users database """
    return map(lambda u: (u.email, u.telegram_id), Users)


def format_lessons(lessons: Iterable,
                   schema: dict=MESSAGE_SCHEMA,
                   city: str="moscow",
                   **kwargs) -> Generator:
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


def format_day_schedule(lessons: Iterable,
                        schema: dict=POST_SCHEMA,
                        **kwargs) -> str:
    """ apply correct day schema to list of this day lessons """
    return schema.format(
        date=f"{DAYS[lessons[0].get('dayOfWeek', 0)]}, "
             f"{lessons[0].get('date', '...')}",
        messages="\n\n".join(lesson for lesson in format_lessons(lessons,
                                                                 **kwargs))
    )


def format_schedule(schedule: Iterable, **kwargs) -> list:
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


def update_schedules(schedules: Iterable,
                     telegram_id: str,
                     next_week: bool=False,
                     rest_time: float=0.01) -> None:
    """ format and save (update) schedules to database (with pause) """
    user = Users.get(telegram_id=telegram_id)
    lessons_obj, _ = user.lessons.get_or_create()
    if not schedules:
        lessons_obj.delete_instance()
        return
    schedule = format_schedule(schedules)

    lessons = dict(zip(TABLE_MAPPING, schedule))
    Lessons.update(
        **lessons,
        upd_dt=datetime.now(),
        is_next_week=next_week
    ).where(Lessons.id == lessons_obj.id).execute()
    time.sleep(rest_time)


def get_and_save(user_info: Iterable) -> None:
    """ pipeline for getting and saving schedules """
    update_schedules(
        schedules=ruz.person_lessons(email=user_info[0]),
        telegram_id=user_info[1]
    )
    update_schedules(
        schedules=ruz.person_lessons(
            email=user_info[0],
            from_date=ruz.get_formated_date(7),
            to_date=ruz.get_formated_date(13)
        ),
        telegram_id=user_info[1],
        next_week=True
    )


def main() -> None:
    pool = Pool(WORKERS_COUNT)
    pool.map(get_and_save, get_users(), chunksize=100)
