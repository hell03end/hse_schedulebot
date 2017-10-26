import re
import time
from collections import Iterator, Iterable
from datetime import datetime
from multiprocessing import Pool

from ruz import RUZ

from bot.models.models import Lecturers, Lessons
from bot.utils.schema import (DAYS, LESSONS_TIMETABLE, MESSAGE_SCHEMA,
                              POST_SCHEMA, TABLE_MAPPING)

from .update_schedules import (format_day_schedule, format_lessons,
                               format_schedule)

api = RUZ()


def check_lecturer(lecturer: dict) -> bool:
    patterns = (re.compile('ераспределенная'), re.compile('акансия'),
                re.compile('!'), re.compile('нагрузка'))
    if not lecturer:
        return False
    for key in ['fio', 'chair']:
        for p in patterns:
            if p.search(lecturer[key]):
                return False
    for word in lecturer['fio'].split()[:1]:
        if not re.match(r'[A-ZА-Я].*', word):
            return False
    return True


def save_lecturers(lecturer: dict) -> None:
    # Checking data
    if not check_lecturer(lecturer):
        return
    lect_dict = {
        'fio': lecturer['fio'],
        'chair': lecturer['chair'],
        'lecturer_id': lecturer['lecturerOid']
    }
    lect_obj, is_created = Lecturers.get_or_create(**lect_dict)
    if not is_created:
        Lecturers.update(
            upd_dt=datetime.now(), **lect_dict
        ).where(
            Lecturers.lecturer_id == lect_obj.lecturer_id
        ).execute()


def get_lecturers_from_api() -> dict:
    """ getting lecturers from api """
    return api.lecturers()


def get_lecturers() -> Iterator:
    return map(lambda l: (l.lecturer_id, l.fio, l.chair), Lecturers)


def fetch_lects_schedule(lecturer_id):
    """ Get a lecturer's schedule from api """
    return api.schedule(lecturerOid=lecturer_id, receiverType=1)


def update_lect_schedules(schedules: Iterable, lect_id: int):
    """ format and save (update) lecturers's schedules to database """
    if not schedules:
        return
    schedule = format_schedule(schedules)
    lessons = dict(zip(TABLE_MAPPING, schedule))

    if not Lecturers.get(Lecturers.lecturer_id == lect_id).lessons:
        lecturer = Lecturers.get(Lecturers.lecturer_id == lect_id)
        lecturer.lessons = Lessons.create(
            **lessons, upd_dt=datetime.now(), is_relative=True)
    else:
        Lessons.update(**lessons, upd_dt=datetime.now()).where(
            Lecturers.get(Lecturers.lecturer_id == lect_id).lessons.id == Lessons.id).execute()
    time.sleep(0.01)


def get_and_save_sched(lect_info: Iterable):
    """ pipeline for getting and saving lecturers schedules """
    update_lect_schedules(
        schedules=fetch_lects_schedule(lecturer_id=lect_info[0]),
        lect_id=lect_info[0]
    )


def main() -> None:
    pool = Pool(5)
    pool.map(save_lecturers, get_lecturers_from_api(), chunksize=35)
    pool.map(get_and_save_sched, get_lecturers(), chunksize=35)
