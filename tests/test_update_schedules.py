# TODO: finish NotImplemented methods

from ruz import RESPONSE_SCHEMA

from bot.models import TABLES, Lessons, Users
from bot.models.tools import create_tables, drop_tables
from bot.models.update_schedules import (api, fetch_schedule,
                                         format_day_schedule, format_lessons,
                                         format_schedule, get_and_save,
                                         get_users, update_schedules)
from bot.utils.schema import MESSAGE_SCHEMA, POST_SCHEMA
from config import PG_CONN
from peewee import PostgresqlDatabase
from playhouse.test_utils import test_database
from tests.commons import create_users
from tests.fixtures import CORRECT_EMAILS, INCORRECT_EMAILS

db_test = PostgresqlDatabase('test_db', **PG_CONN)


def setup_module(self):
    create_tables(TABLES)


def teardown_module(self):
    drop_tables(TABLES)


class TestUpdateDB:
    def setup_class(self):
        self.students = CORRECT_EMAILS['students']
        self.lecturers = CORRECT_EMAILS['lecturers']
        self.schema = RESPONSE_SCHEMA['schedule']
        self.emails = tuple(set(self.lecturers) | set(self.students))

    def test_get_users(self):
        with test_database(db_test, (Users, )):
            create_users()
            emails = {user_info[0] for user_info in get_users()}
            assert emails == set(self.emails)

    def test_fetch_schedule(self):
        schedule = fetch_schedule(self.students[0])
        assert isinstance(schedule, type(self.schema))
        if schedule:
            assert isinstance(schedule[0], type(self.schema[0]))
            for key, param in schedule[0].items():
                if param:
                    assert isinstance(param, self.schema[0][key])

    def test_format_lessons(self) -> NotImplemented:
        return NotImplemented

    def test_format_day_schedule(self) -> NotImplemented:
        return NotImplemented

    def test_format_schedules(self) -> NotImplemented:
        return NotImplemented

    def test_update_schedules(self) -> NotImplemented:
        return NotImplemented

    def test_get_and_save(self):
        with test_database(db_test, (Users, Lessons)):
            create_users()
            for u in Users:
                get_and_save(user_info=(u.email, u.telegram_id, u.student))
            count_lessons = 0
            for lsesson in Lessons:
                assert lsesson
                count_lessons += 1
            assert count_lessons
