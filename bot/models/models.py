import logging
from datetime import datetime

import ruz
from peewee import (BooleanField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, Model, PrimaryKeyField, TextField)
from playhouse.pool import PostgresqlDatabase
from playhouse.shortcuts import RetryOperationalError

from bot.utils.schema import CITIES
from config import PG_CONN


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
    # to store lessons for 2 weeks
    is_next_week = BooleanField(null=True, default=False)
    upd_dt = DateTimeField(default=datetime.now())


class Users(BaseModel):
    telegram_id = IntegerField(unique=1)
    username = CharField(null=True)  # why if it isn't used anywhere?
    email = CharField(null=True)
    city = CharField(null=True)
    show_trains = BooleanField(null=True, default=False)
    lessons = ForeignKeyField(
        Lessons,
        to_field='id',
        null=True,
        on_delete='CASCADE'
    )
    dt = DateTimeField(default=datetime.now())

    def set_city(self, city: str, is_update: bool = False) -> bool:
        if self.city and not is_update:
            return False
        elif city not in CITIES:
            logging.warning("Wrong city: '%s'", city)
            return False
        self.city = CITIES[city]
        return True

    def set_email(self, email: str) -> bool:
        if not ruz.is_valid_hse_email(email):
            logging.warning("Incorrect email: '%s'", email)
            return False
        self.email = email.lower()
        return True


class Lecturers(BaseModel):
    lecturer_id = IntegerField(unique=True)
    fio = CharField(index=True)  # index to faster search by this field
    chair = CharField()  # department in RUZ notation
    lessons = ForeignKeyField(
        Lessons,
        to_field='id',
        null=True,
        on_delete='CASCADE'
    )
