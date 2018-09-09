import logging
from datetime import datetime
from typing import Any, NoReturn

import ruz
from peewee import (AutoField, CharField, DateTimeField, ForeignKeyField,
                    IntegerField, Model, TextField)
from playhouse.pool import PostgresqlDatabase

from config import db


class BaseModel(Model):
    """ Base model with common `id` field """
    id = AutoField()

    def refresh(self) -> Any:
        return type(self).get(self._pk_expr())

    class Meta:
        database = db


class Lessons(BaseModel):
    """ Schedule storage """
    mon = TextField(null=True)
    tue = TextField(null=True)
    wed = TextField(null=True)
    thu = TextField(null=True)
    fri = TextField(null=True)
    sat = TextField(null=True)
    sun = TextField(null=True)
    week_start_dt = CharField()
    update_dt = DateTimeField(default=datetime.now)


class Users(BaseModel):
    """ Users with hse email: students, lecturers, stuff """
    telegram_id = IntegerField(unique=True)
    username = CharField(null=True)
    _email = CharField(null=True)
    registration_dt = DateTimeField(default=datetime.now)
    last_seen_dt = DateTimeField(default=datetime.now)
    lessons = ForeignKeyField(
        Lessons,
        field="id",
        backref="user",
        null=True,
        on_delete="CASCADE"
    )

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> NoReturn:
        value = value.strip().lower()
        if not ruz.utils.is_hse_email(value):
            logging.info("Incorrect email: %s", value)
            return
        self._email = value


class Lecturers(BaseModel):
    """ All HSE lecturers """
    lecturer_id = IntegerField(unique=True)
    fio = CharField(index=True)
    chair = CharField()
    update_dt = DateTimeField(default=datetime.now)
    lessons = ForeignKeyField(
        Lessons,
        field="id",
        backref="lecturer",
        null=True,
        on_delete="CASCADE"
    )

    @staticmethod
    def find_lecturer(query: str) -> NoReturn:
        # [feature] TODO: flexible search of lecturer by part of name
        raise NotImplementedError("Method is not implemented!")
