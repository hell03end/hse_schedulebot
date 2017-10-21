from collections import Collection
from datetime import datetime as dt

from config import PG_CONN
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, PrimaryKeyField, TextField, BooleanField)
from playhouse.pool import PostgresqlDatabase
from playhouse.shortcuts import RetryOperationalError


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
    email = CharField()
    is_student = BooleanField()
    city = CharField(null=True)
    dt = DateTimeField(default=dt.now())


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
    name = CharField()
    # TODO: continue this list


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
