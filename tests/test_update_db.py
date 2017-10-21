# TODO: finish NotImplemented methods

from ruz import RESPONSE_SCHEMA

from config import PG_CONN
from models import TABLES, Lessons, Users, create_tables, drop_tables
from peewee import PostgresqlDatabase
from playhouse.test_utils import test_database
from tests.commons import create_users
from tests.fixtures import CORRECT_EMAILS, INCORRECT_EMAILS
from utils.schema import MESSAGE_SCHEMA, POST_SCHEMA
from utils.update_db import (api, fetch_schedule, format_day_schedule,
                             format_lessons, format_schedule, get_and_save,
                             get_emails, update_schedules)

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

    def test_get_emails(self):
        with test_database(db_test, [Users]):
            create_users()
            emails = {email for email in get_emails()}
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
            get_and_save(self.students[0])
            count_lessons = 0
            for lsesson in Lessons:
                assert lsesson
                count_lessons += 1
            assert count_lessons == 1
