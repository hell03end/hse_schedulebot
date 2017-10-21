import re
import sys
from collections import Collection
from datetime import datetime as dt

from ruz.utils import EMAIL_DOMAINS, EMAIL_PATTERN

from config import PG_CONN
from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, Model, PrimaryKeyField, TextField)
from playhouse.pool import PostgresqlDatabase
from playhouse.shortcuts import RetryOperationalError
from utils.schema import CITIES


class MyRetryDB(RetryOperationalError, PostgresqlDatabase):
    pass


db = MyRetryDB('hse_schedule', **PG_CONN)


class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db


class Users(BaseModel):
    telegram_id = IntegerField(unique=1)
    username = CharField(null=True)
    email = CharField()  # why it is not unique?
    student = BooleanField(default=True)
    city = CharField(null=True)
    dt = DateTimeField(default=dt.now())

    @staticmethod
    def check_email(email: str) -> bool:
        if not re.match(EMAIL_PATTERN, email):
            return False
        domain = email.split('@')[-1]
        if domain not in EMAIL_DOMAINS:
            return False
        return True

    @staticmethod
    def is_student(email: str) -> bool:
        """ check whether email belongs to student or lecturer """
        domain = email.lower().split('@')[-1]  # email should be correct
        if domain == "hse.ru":
            return False
        elif domain == "edu.hse.ru":
            return True
        raise ValueError(f"Wrong domain: {domain}")

    def set_city(self, city: str, update: bool=False) -> None:
        if self.city and not update:
            return
        if city.lower() not in CITIES:
            raise ValueError("Where is no HSE in this city: {city}")
        self.city = city.lower()

    def set_status(self, email: str) -> None:
        self.student = Users.is_student(email)

    def set_email(self, email: str, is_student: bool=True) -> None:
        if '@' not in email:  # try to correct email address
            email += "@edu.hse.ru" if is_student else "@hse.ru"
        if not self.check_email(email):
            raise ValueError("Incorrect email: {email}")
        self.email = email.lower()


class Lessons(BaseModel):
    student = ForeignKeyField(
        Users,
        to_field='telegram_id',
        on_update='CASCADE',
        db_column='student_tg_id'
    )
    monday = TextField(null=True)
    tuesday = TextField(null=True)
    wednesday = TextField(null=True)
    thursday = TextField(null=True)
    friday = TextField(null=True)
    saturday = TextField(null=True)
    sunday = TextField(null=True)
    upd_dt = DateTimeField(default=dt.now())


class Lecturers(BaseModel):
    fio = CharField(index=True)  # index to faster search by this field
    chair = CharField()  # department in RUZ notation
    lecturer_id = IntegerField(unique=True)


TABLES = (Users, Lessons, Lecturers)


def create_tables(tables: Collection) -> None:
    for table in tables:
        if not table.table_exists():
            print("create table: {}".format(table))
            table.create_table()


def drop_tables(tables: Collection) -> None:
    for table in reversed(tables):
        if table.table_exists():
            print("drop table: {}".format(table))
            table.drop_table()


if __name__ == '__main__':
    drop_tables(TABLES)
    create_tables(TABLES)
    print("DONE")
