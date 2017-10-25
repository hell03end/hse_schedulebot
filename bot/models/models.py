import re
from datetime import datetime as dt

from ruz.utils import EMAIL_DOMAINS, EMAIL_PATTERN

from bot.utils.schema import CITIES
from config import PG_CONN
from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, Model, PrimaryKeyField, TextField)
from playhouse.pool import PostgresqlDatabase
from playhouse.shortcuts import RetryOperationalError


class MyRetryDB(RetryOperationalError, PostgresqlDatabase):
    pass


db = MyRetryDB('hse_schedule', **PG_CONN)


class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db


class Lessons(BaseModel):
    monday = TextField(null=True)
    tuesday = TextField(null=True)
    wednesday = TextField(null=True)
    thursday = TextField(null=True)
    friday = TextField(null=True)
    saturday = TextField(null=True)
    sunday = TextField(null=True)
    upd_dt = DateTimeField(default=dt.now())


class Users(BaseModel):
    telegram_id = IntegerField(unique=1)
    username = CharField(null=True)
    email = CharField(null=True)
    is_student = BooleanField(null=True, default=True)
    city = CharField(null=True)
    show_trains = BooleanField(null=True, default=False)
    lessons = ForeignKeyField(
        Lessons,
        to_field='id',
        null=True,
        on_delete='CASCADE'
    )
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
    def is_student_email(email: str) -> bool:
        """ check whether email belongs to student or lecturer """
        domain = email.lower().split('@')[-1]  # email should be correct
        if domain == "hse.ru":
            return False
        elif domain == "edu.hse.ru":
            return True
        raise ValueError(f"Wrong domain: {domain}")

    def set_city(self, city: str, is_update: bool=False) -> None:
        if self.city and not is_update:
            return
        if city not in CITIES:
            raise ValueError("Where is no HSE in this city: {city}")
        self.city = CITIES[city]

    def set_status(self, email: str) -> None:
        self.is_student = Users.is_student_email(email)

    def set_email(self, email: str, is_student: bool=True) -> None:
        if '@' not in email:  # try to correct email address
            email += "@edu.hse.ru" if is_student else "@hse.ru"
        if not self.check_email(email):
            raise ValueError("Incorrect email: {email}")
        self.email = email.lower()


class Lecturers(BaseModel):
    lecturer_id = CharField(unique=True)
    fio = CharField(index=True)  # index to faster search by this field
    chair = CharField()  # department in RUZ notation
    lessons = ForeignKeyField(
        Lessons,
        to_field='id',
        null=True,
        on_delete='CASCADE'
    )
    upd_dt = DateTimeField(default=dt.now())
