import json
import logging
import time
from datetime import datetime, timedelta
from typing import Iterable, NoReturn

import ruz

from models import Lessons, Users


def create_tables(*tables) -> NoReturn:
    for table in tables:
        if not table.table_exists():
            logging.info("Create table:\t%s", table.__name__)
            table.create_table()
        else:
            logging.info("Table exists:\t%s", table.__name__)


def drop_tables(*tables) -> NoReturn:
    for table in reversed(tables):
        if table.table_exists():
            logging.info("Remove table:\t%s", table.__name__)
            table.drop_table(cascade=True)
        else:
            logging.info("Table not found:\t%s", table.__name__)


def remove_fields(obj: dict, to_remove: Iterable) -> dict:
    for key in to_remove:
        del obj[key]
    return obj


def update_user_schedule(user: Users,
                         date_bias: int or float=0,
                         days_count: int = 7,
                         request_delay: float = 0.01) -> NoReturn:
    time.sleep(request_delay)

    date = datetime.now() + timedelta(days=float(date_bias))
    from_date = ruz.utils.get_formated_date(date=date)
    to_date = ruz.utils.get_formated_date(days_count, date=date)

    logging.info("Update schedule from %s to %s for user:%s <%s> [%s]",
                 from_date, to_date, user.id, user.telegram_id, user.email)
    schedule = ruz.person_lessons(user.email, from_date, to_date)
    if schedule is None:
        logging.info("Can't get schedule for user <%s> [%s]",
                     user.telegram_id, user.email)
        return
    elif not schedule:
        return

    # [dev] TODO: move to schema
    useless_fields = (
        "auditoriumOid", "author", "createddate", "dateOfNest", "detailInfo",
        "disciplineOid", "disciplineinplan", "disciplinetypeload", "group",
        "groupOid", "hideincapacity", "isBan", "lecturerOid", "modifieddate",
        "parentschedule", "streamOid", "subGroup", "subGroupOid"
    )
    schedule = map(lambda x: remove_fields(x, useless_fields), schedule)
    schedule = ruz.utils.split_schedule_by_days(schedule)

    lessons = [[] for _ in range(7)]
    for day in schedule:
        lessons[day['dayOfWeek'] - 1] = day['lessons']

    lessons_obj, _ = user.lessons.get_or_create()
    db_fields = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
    lessons = dict(zip(db_fields, map(json.dumps, lessons)))
    Lessons.update(
        **lessons,
        update_dt=date,
        week_start_dt=date + timedelta(days=date.weekday() - 1)
    ).where(Lessons.id == lessons_obj.id).execute()
