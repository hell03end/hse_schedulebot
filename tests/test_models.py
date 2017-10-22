import pytest

from bot.models import TABLES, Lecturers, Lessons, MyRetryDB, Users
from bot.models.tools import create_tables, drop_tables
from bot.utils.schema import CITIES
from config import PG_CONN
from playhouse.test_utils import test_database
from tests.commons import create_users
from tests.fixtures import CORRECT_EMAILS, INCORRECT_EMAILS

db_test = MyRetryDB('test_db', **PG_CONN)


def setup_module(self):
    create_tables(TABLES)


def teardown_module(self):
    drop_tables(TABLES)


class TestUsers:
    def setup_class(self):
        self.students = CORRECT_EMAILS['students']
        self.lecturers = CORRECT_EMAILS['lecturers']
        self.emails = tuple(set(self.lecturers) | set(self.students))

    def test_add_users(self):
        with test_database(db_test, (Users, )):
            create_users()
            count_users = 0
            for user in Users:
                assert user
                count_users += 1
            assert count_users == len(self.emails)

    def test_check_email(self):
        for email in self.emails:
            assert Users.check_email(email)
        for email in INCORRECT_EMAILS:
            assert not Users.check_email(email)

    def test_is_student(self):
        for email in self.students:
            assert Users.is_student(email)
        for email in self.lecturers:
            assert not Users.is_student(email)
        for email in INCORRECT_EMAILS:
            with pytest.raises(ValueError) as excinfo:
                Users.is_student(email)
            assert excinfo

    def test_set_city(self):
        user = Users()
        user.set_city("Moscow")
        assert user.city == "moscow"
        user.set_city("Piter")
        assert user.city == "moscow"
        user.set_city("Piter", update=True)
        assert user.city == "piter"
        with pytest.raises(ValueError) as excinfo:
            user.set_city("Paris", update=True)
        assert excinfo

    def test_set_status(self):
        # almost same as is_student
        user = Users()
        for email in self.students:
            user.set_status(email)
            assert user.student
        for email in self.lecturers:
            user.set_status(email)
            assert not user.student
        for email in INCORRECT_EMAILS:
            with pytest.raises(ValueError) as excinfo:
                user.set_status(email)
            assert excinfo

    def test_set_email(self):
        # almost same as check_email
        user = Users()
        for email in self.emails:
            user.set_email(email)
            assert user.email == email.lower()
        for email in INCORRECT_EMAILS:
            with pytest.raises(ValueError) as excinfo:
                user.set_email(email)
            assert excinfo


class TestLessons:
    pass


class TestLecturers:
    pass
